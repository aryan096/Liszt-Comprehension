import tensorflow as tf
import numpy as np
from collections import defaultdict as ddict


def Attention_Matrix(K, Q, use_mask=False):
    """
    STUDENT MUST WRITE:

    This functions runs a single attention head.

    :param K: is [batch_size x window_size_keys x embedding_size]
    :param Q: is [batch_size x window_size_queries x embedding_size]
    :return: attention matrix
    """

    window_size_queries = Q.get_shape()[1]  # window size of queries
    window_size_keys = K.get_shape()[1]  # window size of keys
    mask = tf.convert_to_tensor(
        value=np.transpose(np.tril(np.ones((window_size_queries, window_size_keys)) * np.NINF, -1), (1, 0)),
        dtype=tf.float32)
    atten_mask = tf.tile(tf.reshape(mask, [-1, window_size_queries, window_size_keys]), [tf.shape(input=K)[0], 1, 1])

    matrix = tf.matmul(Q, tf.reshape(K, shape=[K.shape[0], K.shape[2], K.shape[1]]))
    if use_mask:
        matrix += atten_mask
    matrix = tf.nn.softmax(matrix / np.sqrt(window_size_keys))

    # Remember:
    # - Q is [batch_size x window_size_queries x embedding_size]
    # - K is [batch_size x window_size_keys x embedding_size]
    # - Mask is [batch_size x window_size_queries x window_size_keys]

    # Here, queries are matmuled with the transpose of keys to produce for every query vector, weights per key vector.
    # This can be thought of as: for every query word, how much should I pay attention to the other words in this window?
    # Those weights are then used to create linear combinations of the corresponding values for each query.
    # Those queries will become the new embeddings.

    return matrix


class Atten_Head(tf.keras.layers.Layer):
    def __init__(self, input_size, output_size, use_mask):
        super(Atten_Head, self).__init__()

        self.use_mask = use_mask

        self.K_matrix = self.add_weight(shape=[input_size, output_size], initializer="truncated_normal", trainable=True)
        self.V_matrix = self.add_weight(shape=[input_size, output_size], initializer="truncated_normal", trainable=True)
        self.Q_matrix = self.add_weight(shape=[input_size, output_size], initializer="truncated_normal", trainable=True)

    @tf.function
    def call(self, inputs_for_keys, inputs_for_values, inputs_for_queries):
        """
        STUDENT MUST WRITE:

        This functions runs a single attention head.

        :param inputs_for_keys: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
        :param inputs_for_values: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
        :param inputs_for_queries: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
        :return: tensor of [BATCH_SIZE x (ENG/FRN)_WINDOW_SIZE x output_size ]
        """

        K = tf.tensordot(inputs_for_keys, self.K_matrix, 1)
        # print("K mat shape = {}".format(self.K_matrix.shape))
        # print("K shape = {}".format(K.shape))
        V = tf.tensordot(inputs_for_values, self.V_matrix, 1)
        Q = tf.tensordot(inputs_for_queries, self.Q_matrix, 1)

        atten_matrix = Attention_Matrix(K, Q, self.use_mask)
        # print("atten mat shape = {}".format(atten_matrix.shape))

        out = tf.matmul(atten_matrix, V)
        # print("out shape = {}".format(out.shape))
        return out


class Multi_Headed(tf.keras.layers.Layer):
    # Untested, but I think this is the general architecture?
    def __init__(self, emb_sz, output_size, num_layers, use_mask):
        super(Multi_Headed, self).__init__()


        self.emb_sz = emb_sz
        self.out_size = output_size
        self.num_layers = num_layers
        self.heads = ddict(dict)
        
        #print("size = ", int(emb_sz/num_layers))
        for i in range(num_layers):
            self.heads[i] = Atten_Head(int(emb_sz/num_layers), int(emb_sz/num_layers), use_mask)
        #self.head1 = Atten_Head(int(emb_sz/3), int(emb_sz/3), use_mask)
        #self.head2 = Atten_Head(int(emb_sz/3), int(emb_sz/3), use_mask)
        #self.head3 = Atten_Head(int(emb_sz/3), int(emb_sz/3), use_mask)
        self.linear = tf.keras.layers.Dense(self.out_size)

    @tf.function
    def call(self, inputs_for_keys, inputs_for_values = None, inputs_for_queries = None):
        """
                FOR CS2470 STUDENTS:

                This functions runs a multiheaded attention layer.

                Requirements:
                    - Splits data for 3 different heads of size embed_sz/3
                    - Create three different attention heads
                    - Concatenate the outputs of these heads together
                    - Apply a linear layer

                :param inputs_for_keys: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
                :param inputs_for_values: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
                :param inputs_for_queries: tensor of [batch_size x [ENG/FRN]_WINDOW_SIZE x input_size ]
                :return: tensor of [BATCH_SIZE x (ENG/FRN)_WINDOW_SIZE x output_size ]
                """
        #print(inputs_for_keys)
        if((inputs_for_values==None)&(inputs_for_queries==None)):
            inputs_for_values = inputs_for_keys
            inputs_for_queries = inputs_for_keys
        keys = ddict(dict)
        vals = ddict(dict)
        qs = ddict(dict)
        for i in range((self.num_layers)):
            if(i==self.num_layers):
                keys[i] = inputs_for_keys[:,:,(int(self.emb_sz/self.num_layers)*i):]
                #print("Keys: ", keys[i])
                vals[i] = inputs_for_values[:,:,(int(self.emb_sz/self.num_layers)*i):]
                qs[i] = inputs_for_queries[:,:,(int(self.emb_sz/self.num_layers)*i):]
            else:
                keys[i] = inputs_for_keys[:,:,(int(self.emb_sz/self.num_layers)*i):(int(self.emb_sz/self.num_layers)*(i+1))]
                #print("Keys: ", keys[i])
                vals[i] = inputs_for_values[:,:,(int(self.emb_sz/self.num_layers)*i):(int(self.emb_sz/self.num_layers)*(i+1))]
                qs[i] = inputs_for_queries[:,:,(int(self.emb_sz/self.num_layers)*i):(int(self.emb_sz/self.num_layers)*(i+1))]
        """  
        key_in_1 = inputs_for_keys[:int(self.emb_sz/3)]
        key_in_2 = inputs_for_keys[int(self.emb_sz/3):(2*int(self.emb_sz/3))]
        key_in_3 = inputs_for_keys[(2*int(self.emb_sz/3)):]
        
        val_in_1 = inputs_for_values[:int(self.emb_sz/3)]
        val_in_2 = inputs_for_values[int(self.emb_sz/3):(2*int(self.emb_sz/3))]
        val_in_3 = inputs_for_values[(2*int(self.emb_sz/3)):]
        
        q_in_1 = inputs_for_queries[:int(self.emb_sz/3)]
        q_in_2 = inputs_for_queries[int(self.emb_sz/3):(2*int(self.emb_sz/3))]
        q_in_3 = inputs_for_queries[(2*int(self.emb_sz/3)):]
        
        mult1 = self.head1(key_in_1,val_in_1,q_in_1)
        mult2 = self.head1(key_in_2,val_in_2,q_in_2)
        mult3 = self.head1(key_in_3,val_in_3,q_in_3)
        """
        multi_full = []
        for i in range(self.num_layers):
            #print('multi', i, ' done')
            multi_full.append(self.heads[i](keys[i],vals[i],qs[i]))
        #print("Multi shape: ", len(multi_full))
        multi_full = tf.concat(multi_full,-1)
        #print("Multi shape: ", multi_full)
        out = self.linear(multi_full)

        return out


class Feed_Forwards(tf.keras.layers.Layer):
    def __init__(self, emb_sz):
        super(Feed_Forwards, self).__init__()

        self.layer_1 = tf.keras.layers.Dense(emb_sz, activation='relu')
        self.layer_2 = tf.keras.layers.Dense(emb_sz)

    @tf.function
    def call(self, inputs):
        """
        This functions creates a feed forward network as described in 3.3
        https://arxiv.org/pdf/1706.03762.pdf

        Requirements:
        - Two linear layers with relu between them

        :param inputs: input tensor [batch_size x window_size x embedding_size]
        :return: tensor [batch_size x window_size x embedding_size]
        """
        layer_1_out = self.layer_1(inputs)
        layer_2_out = self.layer_2(layer_1_out)
        return layer_2_out


class Transformer_Block(tf.keras.layers.Layer):
    def __init__(self, emb_sz, is_decoder, multi_headed=True):
        super(Transformer_Block, self).__init__()

        self.ff_layer = Feed_Forwards(emb_sz)
        self.self_atten = Atten_Head(emb_sz, emb_sz, use_mask=is_decoder) if not multi_headed else Multi_Headed(emb_sz,emb_sz,5,use_mask=is_decoder)
        self.is_decoder = is_decoder
        if self.is_decoder:
            self.self_context_atten = Atten_Head(emb_sz, emb_sz, use_mask=False) if not multi_headed else Multi_Headed(emb_sz,emb_sz,5,use_mask=is_decoder)

        self.layer_norm = tf.keras.layers.LayerNormalization(axis=-1)

    @tf.function
    def call(self, inputs, context=None):
        """
        This functions calls a transformer block.

        There are two possibilities for when this function is called.
            - if self.is_decoder == False, then:
                1) compute unmasked attention on the inputs
                2) residual connection and layer normalization
                3) feed forward layer
                4) residual connection and layer normalization

            - if self.is_decoder == True, then:
                1) compute MASKED attention on the inputs
                2) residual connection and layer normalization
                3) computed UNMASKED attention using context
                4) residual connection and layer normalization
                5) feed forward layer
                6) residual layer and layer normalization

        If the multi_headed==True, the model uses multiheaded attention (Only 2470 students must implement this)

        :param inputs: tensor of [BATCH_SIZE x (ENG/FRN)_WINDOW_SIZE x EMBEDDING_SIZE ]
        :context: tensor of [BATCH_SIZE x FRENCH_WINDOW_SIZE x EMBEDDING_SIZE ] or None
            default=None, This is context from the encoder to be used as Keys and Values in self-attention function
        """

        #with av.trans_block(self.is_decoder):
        atten_out = self.self_atten(inputs, inputs, inputs)
        atten_out += inputs
        atten_normalized = self.layer_norm(atten_out)

        if self.is_decoder:
            assert context is not None, "Decoder blocks require context"
            #print("CONTEXT: ",context)
            context_atten_out = self.self_context_atten(context, context, atten_normalized)
            context_atten_out += atten_normalized
            atten_normalized = self.layer_norm(context_atten_out)

        ff_out = self.ff_layer(atten_normalized)
        ff_out += atten_normalized
        ff_norm = self.layer_norm(ff_out)

        return tf.nn.relu(ff_norm)


class Position_Encoding_Layer(tf.keras.layers.Layer):
    def __init__(self, window_sz, emb_sz):
        super(Position_Encoding_Layer, self).__init__()
        self.positional_embeddings = self.add_weight("pos_embed", shape=[window_sz, emb_sz])

    @tf.function
    def call(self, x):
        """
        Adds positional embeddings to word embeddings.

        :param x: [BATCH_SIZE x (ENG/FRN)_WINDOW_SIZE x EMBEDDING_SIZE ] the input embeddings fed to the encoder
        :return: [BATCH_SIZE x (ENG/FRN)_WINDOW_SIZE x EMBEDDING_SIZE ] new word embeddings with added positional encodings
        """
        return x + self.positional_embeddings

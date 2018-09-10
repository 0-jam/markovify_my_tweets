### 実行に時間かかる
# embedded_dim = 256, units = 1024のとき、epochごとに30分くらいかかる
## ライブラリをロード
import tensorflow as tf
tf.enable_eager_execution()

import numpy as np
import random
import re
import time
import argparse
import unidecode

# オプション設定・取得
parser = argparse.ArgumentParser(description="Generate sentence with RNN.")
parser.add_argument("input", type=str, help="input file path")
parser.add_argument("start_string", type=str, help="generation start with this string")
parser.add_argument("-o", "--output", type=str, default="out_rnn.txt", help="output file path (default: 'out_rnn.txt')")
parser.add_argument("-e", "--epochs", type=int, default=5, help="the number of epochs (default: 5)")
parser.add_argument("-g", "--gen_size", type=int, default=1000, help="the size of text that you want to generate (default: 1000)")
args = parser.parse_args()

with open(args.input) as file:
    # text = unidecode.unidecode(file.read())
    text = file.read()

# テキスト中に現れる文字を取得
unique = sorted(set(text))
# 各文字に数字を割り当てる
char2idx = {char:index for index, char in enumerate(unique)}
idx2char = {index:char for index, char in enumerate(unique)}

# 文の長さを指定
max_length = 100
vocab_size = len(unique)
embedding_dim = 128
# RNN (Recursive Neural Network) ノード数
units = 512
batch_size = 64
# シャッフル用バッファサイズ
buffer_size = 10000

## 入力・出力用テンソル作成
input_text = []
target_text = []

for i in range(0, len(text) - max_length, max_length):
    input = text[i:i + max_length]
    target = text[i + 1:i + 1 + max_length]

    input_text.append([char2idx[j] for j in input])
    target_text.append([char2idx[k] for k in target])

## バッチを作ってシャッフルする
dataset = tf.data.Dataset.from_tensor_slices((input_text, target_text)).shuffle(buffer_size)
dataset = dataset.batch(batch_size, drop_remainder=True)

class Model(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, units, batch_size):
        super(Model, self).__init__()
        self.units = units
        self.batch_sz = batch_size
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)

        # CUDAが使えるか確認
        if tf.test.is_gpu_available():
            self.gru = tf.keras.layers.CuDNNGRU(
                self.units,
                return_sequences=True,
                return_state=True,
                recurrent_initializer='glorot_uniform'
            )
        else:
            self.gru = tf.keras.layers.GRU(
                self.units,
                return_sequences=True,
                return_state=True,
                recurrent_activation='sigmoid',
                recurrent_initializer='glorot_uniform'
            )

        self.fc = tf.keras.layers.Dense(vocab_size)

    def call(self, x, hidden):
        x = self.embedding(x)

        # output_shape = (batch_size, max_length, hidden_size)
        # states_shape = (batch_size, hidden_size)

        # statesにモデルの状態を格納
        # 訓練中に毎回渡される
        output, states = self.gru(x, initial_state=hidden)

        # Densely-connected層に渡せる形にデータを整形
        # 整形後：(batch_size * max_length, hidden)
        output = tf.reshape(output, (-1, output.shape[2]))

        # output shape after the dense layer is (batch_size * max_length, vocab_size)
        x = self.fc(output)

        return x, states

## モデル作成
model = Model(vocab_size, embedding_dim, units, batch_size)
## 最適化関数・損失関数を設定
optimizer = tf.train.AdamOptimizer()

def loss_function(real, preds):
    # one-hotベクトルを生成しなくていいようにsparse_softmax_cross_entropyを使う
    return tf.losses.sparse_softmax_cross_entropy(labels=real, logits=preds)

## モデルを訓練させる
epochs = args.epochs

for epoch in range(epochs):
    start = time.time()

    # epochごとに隠れ状態(hidden state)を初期化
    hidden = model.reset_states()

    for (batch, (input, target)) in enumerate(dataset):
        with tf.GradientTape() as tape:
            # モデルに隠れ状態を与える
            predictions, hidden = model(input, hidden)

            # 損失関数に対象を予期させる？ように対象を整形する
            # (reshape target to make loss function expect the target)
            target = tf.reshape(target, (-1,))
            loss = loss_function(target, predictions)

        gradients = tape.gradient(loss, model.variables)
        optimizer.apply_gradients(zip(gradients, model.variables), global_step = tf.train.get_or_create_global_step())

        print("Epoch: {} / {}, Batch: {}, Loss: {:.4f}".format(epoch + 1, epochs, batch + 1, loss))

    print("Time taken for 1 epoch {} sec \n".format(time.time() - start))

## 訓練済みモデルで予測
gen_size = 10000
generated_text = ''
start_string = args.start_string
# start_stringを番号にする
input_eval = tf.expand_dims([char2idx[s] for s in start_string], 0)
# temperaturesが大きいほど予測しにくい(surprising)テキストが生成される
temperature = 1.0

# 隠れ状態の形：(batch_size, units)
hidden = [tf.zeros((1, units))]

for i in range(gen_size):
    # print("prediction {} / {}".format(i + 1, gen_size))
    predictions, hidden = model(input_eval, hidden)

    # モデルから返ってきた単語を予測するのに偏微分を使う
    predictions = predictions / temperature
    predicted_id = tf.multinomial(tf.exp(predictions), num_samples = 1)[0][0].numpy()

    # 予測された言葉と以前の隠れ状態をモデルに次の入力として渡す
    input_eval = tf.expand_dims([predicted_id], 0)

    generated_text += idx2char[predicted_id]

with open(args.output, 'w') as out:
    out.write(start_string + generated_text)

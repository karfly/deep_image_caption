from keras.applications import ResNet50, VGG16
from keras.applications.resnet50 import preprocess_input
from keras.models import Sequential
from keras.layers import Flatten, Dense, RepeatVector, LSTM, Embedding, TimeDistributed, Merge


def build_image_encoder(image_height, image_width, n_channels):
    model = Sequential()
    model.add(VGG16(include_top=True, weights='imagenet', input_shape=(image_height, image_width, n_channels)))
    model.add(Flatten())

    return model


def build_caption_model(embedding_dim, caption_length, vocabulary_size,
                        image_height=224, image_width=224, n_channels=3):
    image_encoder = build_image_encoder(image_height, image_width, n_channels)
    image_encoder.trainable = False

    image_model = Sequential()
    for layer in image_encoder.layers:
        image_model.add(layer)
    image_model.add(Dense(embedding_dim, activation='relu'))
    image_model.add(RepeatVector(caption_length))

    language_model = Sequential()
    language_model.add(Embedding(vocabulary_size, 256, input_length=caption_length))
    language_model.add(LSTM(256,return_sequences=True))
    language_model.add(TimeDistributed(Dense(embedding_dim)))

    caption_model = Sequential()
    caption_model.add(Merge([image_model, language_model], mode='concat'))
    caption_model.add(LSTM(256, return_sequences=False))
    caption_model.add(Dense(vocabulary_size, activation='softmax'))

    caption_model.compile(loss='categorical_crossentropy', optimizer='rmsprop',
                          metrics=['accuracy'])

    return caption_model
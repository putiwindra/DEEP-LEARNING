# -*- coding: utf-8 -*-
"""DEEP_LEARNING_CNN_2_DenseNet

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/147HVvNYC_KcZaK-5HqeZE2mkWb_1fUo-
"""

pip install streamlit

import streamlit
import numpy as np
import pandas as pd
import os

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import matplotlib.pyplot as plt

train_dir = '/content/drive/MyDrive/xray_dataset_covid19/train'
test_dir = '/content/drive/MyDrive/xray_dataset_covid19/test'

#AUGMENTASI
import os
import matplotlib.pyplot as plt

# Membuat direktori 'preview' jika belum ada
if not os.path.exists('preview'):
    os.makedirs('preview')

# Membuat ImageDataGenerator untuk augmentasi
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Gunakan train_datagen yang baru dibuat
augmented_images = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=10,  # Mengubah batch_size menjadi 10
    class_mode='binary',
    save_to_dir='preview',
    save_prefix='augmented',
    save_format='jpeg'
)

# Menentukan jumlah gambar hasil augmentasi
augmented_images_dir = 'preview'
augmented_images_count = len([file for file in os.listdir(augmented_images_dir) if file.startswith('augmented')])
print(f"Jumlah gambar hasil augmentasi: {augmented_images_count}")

# Menampilkan beberapa contoh gambar yang telah diubah
fig, axes = plt.subplots(1, 10, figsize=(20, 4))  # Menyesuaikan jumlah subplot menjadi 10
for i in range(10):  # Menyesuaikan jumlah iterasi menjadi 10
    augmented_image, _ = augmented_images.next()
    axes[i].imshow(augmented_image[0])
    axes[i].axis('off')
plt.show()

"""#Pemodelan"""

from tensorflow.keras.applications import DenseNet121

# Load pre-trained DenseNet-121 model
base_model = DenseNet121(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze the layers in the base DenseNet model
for layer in base_model.layers:
    layer.trainable = False

# Add custom classification head
x = base_model.output
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(512, activation='relu')(x)
x = tf.keras.layers.Dropout(0.5)(x)
predictions = tf.keras.layers.Dense(1, activation='sigmoid')(x)

# Combine the base DenseNet model with custom classification head
model = tf.keras.models.Model(inputs=base_model.input, outputs=predictions)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)
model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(train_generator, steps_per_epoch=len(train_generator), epochs=50, validation_data=test_generator, validation_steps=len(test_generator))
# Calculate confusion matrix and metrics
cm = confusion_matrix(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

# Plot confusion matrix
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title("Confusion matrix")
plt.colorbar()
tick_marks = np.arange(2)
plt.xticks(tick_marks, ['Normal', 'Pneumonia'], rotation=45)
plt.yticks(tick_marks, ['Normal', 'Pneumonia'])

plt.tight_layout()
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()

print("F1 Score: ", f1)
print("Precision: ", precision)
print("Recall: ", recall)

# Plot the accuracy and loss
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()

# Display the model summary
model.summary()

# Penjelasan untuk setiap layer
for i, layer in enumerate(model.layers):
    print(f"\nLayer {i} - {layer.name}:")
    print(f"Type: {layer.__class__.__name__}")
    print(f"Output Shape: {layer.output_shape}")
    print(f"Parameters: {layer.count_params()}")
    print(f"Trainable: {layer.trainable}")

from google.colab import drive
drive.mount('/content/drive')

test_loss, test_acc = model.evaluate(test_generator, steps=len(test_generator))
print('\nTest accuracy:', test_acc)

"""# **Normal**"""

sample_image_path = '/content/drive/MyDrive/xray_dataset_covid19/test/NORMAL/NORMAL2-IM-0072-0001.jpeg'
sample_image = tf.keras.preprocessing.image.load_img(sample_image_path, target_size=(224, 224))
sample_image = tf.keras.preprocessing.image.img_to_array(sample_image)
sample_image = sample_image / 255.0
sample_image = tf.expand_dims(sample_image, 0)
prediction = model.predict(sample_image)
print('Prediction:', prediction)

plt.imshow(sample_image[0])
plt.title('PNEUMONIA' if prediction[0][0] > 0.5 else 'NORMAL')

plt.show()

"""# **Pneumonia**"""

sample_image_path = '/content/drive/MyDrive/xray_dataset_covid19/test/PNEUMONIA/303.jpg'
sample_image = tf.keras.preprocessing.image.load_img(sample_image_path, target_size=(224, 224))
sample_image = tf.keras.preprocessing.image.img_to_array(sample_image)
sample_image = sample_image / 255.0
sample_image = tf.expand_dims(sample_image, 0)
prediction = model.predict(sample_image)
print('Prediction:', prediction)

plt.imshow(sample_image[0])
plt.title('PNEUMONIA' if prediction[0][0] > 0.5 else 'NORMAL')
plt.show()

"""* Nilai mendekati 0: Model yakin bahwa gambar tersebut tidak termasuk dalam kelas positif (Non-COVID-19).
* Nilai mendekati 1: Model yakin bahwa gambar tersebut termasuk dalam kelas positif (COVID-19).

# Pengujian Model
"""

import random
import os
import matplotlib.pyplot as plt

# Ambil path direktori test
test_normal_dir = '/content/drive/MyDrive/xray_dataset_covid19/test/NORMAL'
test_pneumonia_dir = '/content/drive/MyDrive/xray_dataset_covid19/test/PNEUMONIA'

# Ambil gambar secara acak dari setiap direktori
normal_images = [os.path.join(test_normal_dir, file) for file in os.listdir(test_normal_dir)]
pneumonia_images = [os.path.join(test_pneumonia_dir, file) for file in os.listdir(test_pneumonia_dir)]

# Menggabungkan semua gambar
all_images = normal_images + pneumonia_images

# Pilih 2 gambar acak
random_image_paths = random.sample(all_images, 2)

# Memuat, memproses, dan menampilkan gambar serta prediksinya
for i, random_image_path in enumerate(random_image_paths):
    sample_image = tf.keras.preprocessing.image.load_img(random_image_path, target_size=(224, 224))
    sample_image = tf.keras.preprocessing.image.img_to_array(sample_image)
    sample_image = sample_image / 255.0
    sample_image = tf.expand_dims(sample_image, 0)
    prediction = model.predict(sample_image)
    print(f'Prediction {i + 1}:', prediction)

    plt.subplot(1, 2, i + 1)
    plt.imshow(sample_image[0])
    plt.title('PNEUMONIA' if prediction[0][0] > 0.5 else 'NORMAL')

plt.show()
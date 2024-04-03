import os
import numpy as np
import tensorflow as tf
from PIL import Image

resolution = (224, 224)


def load_image(filepath):
    img = Image.open(filepath)
    img = img.resize(resolution)  # Resize to match model input size if necessary
    img = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    return img


def predict_direction(model, img):
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    predictions = model.predict(img)
    direction = np.argmax(predictions[0])  # Get index of maximum prediction
    return direction


def get_actual_direction(filename):
    # Extract direction part from filename (zzz)
    direction = filename.split('_')[-1].split('.')[0]
    # Convert direction to numeric value
    if direction == 'forward':
        return 0
    elif direction == 'leftTurn':
        return 1
    elif direction == 'rightTurn':
        return 2
    elif direction == 'stop':
        return 3
    else:
        return None


def main():
    model = tf.keras.models.load_model('trained_models/model_goodResult.keras')
    image_dir = 'C:/Users/tomca/Desktop/New folder'

    total_predictions = 0
    correct_predictions = 0

    for filename in os.listdir(image_dir):
        if filename.endswith('.jpg'):
            filepath = os.path.join(image_dir, filename)
            img = load_image(filepath)
            prediction = predict_direction(model, img)
            actual_direction = get_actual_direction(filename)
            if actual_direction is not None:
                total_predictions += 1
                if prediction == actual_direction:
                    correct_predictions += 1
                    print("Prediction for", filename, "was correct.")
                else:
                    print("Prediction for", filename, "was incorrect. Predicted:", prediction, "Actual:",
                          actual_direction)
            else:
                print("Invalid filename format for", filename)

    accuracy = correct_predictions / total_predictions * 100 if total_predictions > 0 else 0
    print("Accuracy:", accuracy, "%")


if __name__ == '__main__':
    main()

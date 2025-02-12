import cv2
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

# Load the model and processor from Hugging Face
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def is_golf_swing(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []

    # Extract a few frames to analyze
    for _ in range(10):  # Adjust the number of frames as needed
        success, frame = cap.read()
        if not success:
            break
        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        frames.append(pil_image)

    cap.release()

    # Check if MPS is available
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    
    # Load the model and processor from Hugging Face
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Prepare the inputs for the model
    inputs = processor(text=["a golf swing"], images=frames, return_tensors="pt", padding=True).to(device)

    # Get the outputs from the model
    with torch.no_grad():
        outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)

    # Check if a golf swing is detected
    golf_swing_detected = any(prob[0] > 0.5 for prob in probs)  # Adjust threshold as needed

    return golf_swing_detected

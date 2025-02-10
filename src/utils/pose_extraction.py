import mediapipe as mp
import cv2

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def extract_pose(frame):
    with mp_pose.Pose(min_detection_confidence=0.5) as pose:
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            pose_data = {}
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                # Process each landmark
                print(f"Landmark {idx}: {landmark.x}, {landmark.y}, {landmark.z}")
                pose_name = get_pose_name(idx)
                pose_data[pose_name] = {"x": landmark.x, "y": landmark.y, "z": landmark.z}
            else:
                pose_data = {}

            return pose_data

def get_pose_name(idx):
    pose_names = {
        0: "nose",
        1: "left_eye_inner",
        2: "left_eye",
        3: "left_eye_outer",
        4: "right_eye_inner",
        5: "right_eye",
        6: "right_eye_outer",
        7: "left_ear",
        8: "right_ear",
        9: "mouth_left",
        10: "mouth_right",
        11: "left_shoulder",
        12: "right_shoulder",
        13: "left_elbow",
        14: "right_elbow",
        15: "left_wrist",
        16: "right_wrist",
        17: "left_pinky",
        18: "right_pinky",
        19: "left_index",
        20: "right_index",
        21: "left_thumb",
        22: "right_thumb",
        23: "left_hip",
        24: "right_hip",
        25: "left_knee",
        26: "right_knee",
        27: "left_ankle",
        28: "right_ankle",
        29: "left_heel",
        30: "right_heel",
        31: "left_foot_index",
        32: "right_foot_index"
    }
    return pose_names.get(idx, f"Invalid pose landmark index: {idx}")
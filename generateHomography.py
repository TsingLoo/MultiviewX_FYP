import cv2
import numpy as np
import os
import xml.etree.ElementTree as ET

intrinsic_path = r"C:\Users\73646\Desktop\calibrations\intrinsic_zero"
intrinsic_xml = r"intr_CVLab3.xml"


extrinsic_path = r"C:\Users\73646\Desktop\calibrations\extrinsic"
extrinsic_xml = r"extr_CVLab3.xml"

fp_calibration = cv2.FileStorage(os.path.join(intrinsic_path, f'{intrinsic_xml}'),
                                 flags=cv2.FILE_STORAGE_READ)

# 取得给定的相机内参
cameraMatrix, distCoeffs = fp_calibration.getNode('camera_matrix').mat(), fp_calibration.getNode(
    'distortion_coefficients').mat()

print(cameraMatrix)

fp_calibration.release()


# Parse the XML file
tree = ET.parse(os.path.join(extrinsic_path, extrinsic_xml))
root = tree.getroot()

# Extract and convert the rotation vector (rvec)
rvec_text = root.find('rvec').text.strip()
rvec = np.array([float(num) for num in rvec_text.split()])

# Extract and convert the translation vector (tvec)
tvec_text = root.find('tvec').text.strip()
tvec = np.array([float(num) for num in tvec_text.split()])

print("Rotation Vector (rvec):", rvec)
print("Translation Vector (tvec):", tvec)

R, _ = cv2.Rodrigues(rvec)

# Assuming the ground plane is Z=0 in the world coordinate system
# Extract the relevant parts of the rotation matrix (first two columns)
R_3x2 = R[:, :2]

# Construct a 3x3 homography matrix
# The third column is the translation vector
H = np.hstack((R_3x2, tvec.reshape(-1, 1)))

# Multiply by the intrinsic matrix to get the final homography matrix
H = np.dot(cameraMatrix, H)

# Normalize the homography matrix
#H /= H[2, 2]


# H is now the homography matrix from the camera view to the groun
print("Homography Matrix:")
print(H)
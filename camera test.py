import cv2

# Use CAP_DSHOW to avoid MSMF errors on Windows
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Unable to access camera.")
    exit()

print("✅ Camera is working. Press ESC to exit.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame.")
        break

    cv2.imshow("Camera Test", frame)

    # Exit on pressing ESC (27)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

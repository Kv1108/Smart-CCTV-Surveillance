import cv2
import numpy as np

# Open camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip frame for natural interaction
    frame = cv2.flip(frame, 1)

    # Define Region of Interest (ROI) for hand
    roi = frame[100:400, 100:400]  # Crop region
    cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)

    # Convert ROI to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Define skin color range in HSV
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Create mask for skin
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Blur to reduce noise
    mask = cv2.GaussianBlur(mask, (5, 5), 100)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours and len(contours) > 0:
        # Take the largest contour (hand)
        contour = max(contours, key=lambda x: cv2.contourArea(x))

        # Draw contour
        cv2.drawContours(roi, [contour], -1, (255, 0, 0), 2)

        # Convex hull
        hull = cv2.convexHull(contour)
        cv2.drawContours(roi, [hull], -1, (0, 255, 0), 2)

        # Convexity defects
        hull_indices = cv2.convexHull(contour, returnPoints=False)
        if len(hull_indices) > 3:
            defects = cv2.convexityDefects(contour, hull_indices)

            if defects is not None:
                count_defects = 0
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])

                    # Apply cosine rule to find angle
                    a = np.linalg.norm(np.array(end) - np.array(start))
                    b = np.linalg.norm(np.array(far) - np.array(start))
                    c = np.linalg.norm(np.array(end) - np.array(far))
                    angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c)) * 57

                    # If angle < 90°, treat as a finger
                    if angle <= 90:
                        count_defects += 1
                        cv2.circle(roi, far, 4, (0, 0, 255), -1)

                # Map defects → gestures
                if count_defects == 0:
                    cv2.putText(frame, "Fist / One", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif count_defects == 1:
                    cv2.putText(frame, "Two Fingers", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif count_defects == 2:
                    cv2.putText(frame, "Three Fingers", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif count_defects == 3:
                    cv2.putText(frame, "Four Fingers", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "Open Palm", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show windows
    cv2.imshow("Hand Gesture Recognition", frame)
    cv2.imshow("Mask (Skin Detection)", mask)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

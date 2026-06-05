import os
import cv2
from main import ProToolOrchestrator


def test_complete_pipeline_flow():
    input_image = "test_screen.png"
    output_image = "result.png"

    assert os.path.exists(input_image), (
        f"Missing required test image: {input_image}"
    )

    assert os.path.exists("models/best.pt"), (
        "Missing YOLO model: models/best.pt"
    )

    orchestrator = ProToolOrchestrator(is_ci_environment=True)

    frame = cv2.imread(input_image)

    assert frame is not None, (
        f"Failed to load image: {input_image}"
    )

    result = orchestrator.process_frame(frame)

    cv2.imwrite(output_image, result)

    assert os.path.exists(output_image), (
        "Failed to create result.png"
    )

    output = cv2.imread(output_image)

    assert output is not None, (
        "result.png was created but could not be read"
    )

    assert output.shape[0] > 0
    assert output.shape[1] > 0

    print("YOLO Detection Pipeline Verified Successfully!")


if __name__ == "__main__":
    test_complete_pipeline_flow()

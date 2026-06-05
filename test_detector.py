# test_detector.py
import os
import pytest
from main import ProToolOrchestrator

def test_complete_pipeline_flow():
    # التأكد التام من وجود ملف الصورة المرفوعة في الـ Root
    input_image = "test_screen.png"
    output_image = "result.png"
    
    assert os.path.exists(input_image), f"ملف {input_image} مش موجود في الـ Root يا صاحبي، ارفعه الأول!"
    
    # تشغيل الأوركسترا كاملة في وضع الـ CI
    orchestrator = ProToolOrchestrator(is_ci_environment=True)
    orchestrator.run_static_test(input_image, output_image)
    
    # التأكد من خروج الـ Artifact بنجاح وعدم حدوث كراش
    assert os.path.exists(output_image), "البرنامج فشل في تكوين ملف النتيجة result.png"
    print("CI Pipeline Workflow Verified Successfully!")

if __name__ == "__main__":
    test_complete_pipeline_flow()

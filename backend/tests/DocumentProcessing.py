import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.UploadService import UploadService
from fastapi import UploadFile
import asyncio
import tempfile


class ProcessingTest:

    _uploadService = None

    @classmethod
    def init(cls):
        if not cls._uploadService:
            cls._uploadService = UploadService()
        return cls._uploadService

    def __init__(self):
        self.uploadService = self.init()
        self.test_file_path = "/Users/padam/Downloads/complaint_partition_sale.pdf"

    def _create_upload_file(self, file_path: str) -> UploadFile:
        """
        Create a mock UploadFile object for testing
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Test file not found: {file_path}")
        
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Create a simple mock UploadFile
        class MockUploadFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
                self.size = len(content)
            
            async def read(self, size: int = -1):
                return self.content
        
        filename = Path(file_path).name
        return MockUploadFile(filename, content)

    async def test_validate_file(self):
        """
        Test file validation functionality
        """
        print("\n=== Testing validate_file ===")
        try:
            upload_file = self._create_upload_file(self.test_file_path)
            print(f"Testing file validation for: {upload_file.filename}")
            
            # Test validation
            result = await self.uploadService.validate_file(upload_file)
            print(f"✅ File validation passed: {upload_file.filename}")
            print(f"File size: {upload_file.size} bytes")
            return True
            
        except Exception as e:
            print(f"❌ File validation failed: {e}")
            return False

    def test_split_text_into_chunks(self):
        """
        Test text splitting functionality
        """
        print("\n=== Testing split_text_into_chunks ===")
        try:
            # Sample text for testing
            sample_text = """
            This is a legal document with multiple sections. 
            It contains important terms and conditions that need to be analyzed.
            
            Section 1: Introduction
            This section introduces the parties involved in the agreement.
            
            Section 2: Terms and Conditions
            This section outlines the specific terms of the agreement.
            
            Section 3: Liability and Risk
            This section discusses liability and risk factors.
            """
            
            print(f"Sample text length: {len(sample_text)} characters")
            
            # Test chunking with different parameters
            chunks = self.uploadService.split_text_into_chunks(sample_text, chunk_size=200, chunk_overlap=50)
            
            print(f"✅ Text split into {len(chunks)} chunks")
            for i, chunk in enumerate(chunks):
                print(f"Chunk {i+1}: {len(chunk)} chars - {chunk[:50]}...")
            
            return chunks
            
        except Exception as e:
            print(f"❌ Text splitting failed: {e}")
            return None

    async def test_analyze_document_with_llm(self):
        """
        Test LLM document analysis functionality
        """
        print("\n=== Testing analyze_document_with_llm ===")
        try:
            # Sample legal text for analysis
            sample_legal_text = """
            RENTAL AGREEMENT
            
            This Rental Agreement is entered into between John Doe (Landlord) and Jane Smith (Tenant).
            
            Terms:
            1. Monthly rent: $1,500 due on the 1st of each month
            2. Security deposit: $1,500 (refundable)
            3. Lease term: 12 months starting January 1, 2024
            4. Late fee: $50 for payments after the 5th
            5. Tenant responsible for utilities
            6. No pets allowed without written consent
            7. 30-day notice required for termination
            """
            
            print(f"Analyzing sample legal text ({len(sample_legal_text)} characters)")
            
            analysis = await self.uploadService.analyze_document_with_llm(sample_legal_text)
            
            print("✅ LLM Analysis completed:")
            print(f"Document Type: {analysis.get('Document_Type', 'N/A')}")
            print(f"Risk Score: {analysis.get('Risk_Assessment', {}).get('Risk_Score', 'N/A')}")
            print(f"Key Highlights: {len(analysis.get('Key_Highlights', []))} items")
            print(f"Key Terms: {len(analysis.get('Key_Terms', []))} items")
            
            return analysis
            
        except Exception as e:
            print(f"❌ LLM analysis failed: {e}")
            return None

    async def test_process_pdf(self):
        """
        Test PDF processing functionality
        """
        print("\n=== Testing _process_pdf ===")
        try:
            if not os.path.exists(self.test_file_path):
                print(f"❌ Test file not found: {self.test_file_path}")
                return None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"Processing PDF: {self.test_file_path}")
                
                path = os.path.join("", self.test_file_path)
                extracted_text = await self.uploadService._process_pdf(
                   path , temp_dir
                )
                
                print(f"✅ PDF processing completed:")
                print(f"Extracted text length: {len(extracted_text)} characters")
                print(f"Text preview: {extracted_text[:200]}...")
                
                return extracted_text
                
        except Exception as e:
            print(f"❌ PDF processing failed: {e}")
            return None

    async def test_process_document_full(self):
        """
        Test the complete document processing workflow
        """
        print("\n=== Testing process_document (Full Workflow) ===")
        try:
            upload_file = self._create_upload_file(self.test_file_path)
            print(f"Testing full document processing for: {upload_file.filename}")
            
            result = await self.uploadService.process_document(upload_file)
            
            print("✅ Full document processing completed:")
            print(f"Success: {result.body.get('success', False) if hasattr(result, 'body') else 'Unknown'}")
            
            # If result is a JSONResponse, we need to extract the content
            if hasattr(result, 'body'):
                import json
                content = json.loads(result.body.decode())
                print(f"Document ID: {content.get('document_id', 'N/A')}")
                print(f"File type: {content.get('file_type', 'N/A')}")
                print(f"Text chunks: {content.get('metadata', {}).get('total_chunks', 'N/A')}")
                print(f"Processing time: {content.get('metadata', {}).get('processing_time_seconds', 'N/A')}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Full document processing failed: {e}")
            return None

    async def run_all_tests(self):
        """
        Run all individual tests
        """
        print("=" * 60)
        print("🧪 Starting Individual Function Tests")
        print("=" * 60)
        
        if not os.path.exists(self.test_file_path):
            print(f"❌ Test file not found: {self.test_file_path}")
            print("Please ensure the file exists before running tests.")
            return
        
        test_results = {}
        
        # # Test 1: File validation
        # test_results['validate_file'] = await self.test_validate_file()
        
        # # Test 2: Text splitting
        # test_results['split_text'] = self.test_split_text_into_chunks() is not None
        
        # # Test 3: LLM analysis
        # test_results['llm_analysis'] = await self.test_analyze_document_with_llm() is not None
        
        # # Test 4: PDF processing
        # test_results['pdf_processing'] = await self.test_process_pdf() is not None
        
        # Test 5: Full document processing
        test_results['full_processing'] = await self.test_process_document_full() is not None
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:20} | {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        print("=" * 60)

    def run_manual_tests(self):
        """
        Run all manual tests - wrapper for async function
        """
        asyncio.run(self.run_all_tests())


# Helper function to run tests easily
def run_tests():
    """
    Convenience function to run the tests
    """
    test_instance = ProcessingTest()
    test_instance.run_manual_tests()


if __name__ == "__main__":
    run_tests()




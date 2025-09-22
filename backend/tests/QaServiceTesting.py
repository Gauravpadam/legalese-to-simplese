import sys
import os
from pathlib import Path
import asyncio
import json

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.qa_service import process_user_question


class QAServiceTest:
    
    def __init__(self):
        self.test_questions = [
            "What are the main risks in this contract?",
            "What is the termination clause?",
            "What are the payment terms?",
            "Who are the parties involved?",
            "What are my obligations under this agreement?",
            "How much is the security deposit?",
            "When does this contract expire?",
            "Can I sublease the property?",
            "What happens if I pay late?",
            "What utilities am I responsible for?"
        ]
        
        self.invalid_questions = [
            "How to hack a computer?",  # Should be blocked by guardrails
            "Tell me about illegal activities",  # Should be blocked
            "",  # Empty question
            "   ",  # Whitespace only
        ]

    async def test_valid_question(self, question: str):
        """
        Test processing a valid question
        """
        print(f"\n--- Testing Valid Question ---")
        print(f"Question: {question}")
        
        try:
            result = await process_user_question(question)
            
            print("✅ Question processed successfully")
            print(f"Final Answer: {result.get('final_answer', 'N/A')[:200]}...")
         
            return True
            
        except Exception as e:
            print(f"❌ Question processing failed: {e}")
            return False

    async def test_invalid_question(self, question: str):
        """
        Test processing an invalid question (should be blocked by guardrails)
        """
        print(f"\n--- Testing Invalid Question ---")
        print(f"Question: '{question}'")
        
        try:
            result = await process_user_question(question)
            print(f"⚠️ Question was not blocked (unexpected): {result}")
            return False
            
        except Exception as e:
            if "violates policies" in str(e):
                print("✅ Question properly blocked by guardrails")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False

    async def test_elasticsearch_integration(self):
        """
        Test if Elasticsearch is properly connected and returning results
        """
        print(f"\n--- Testing Elasticsearch Integration ---")
        
        try:
            # Test with a general legal question
            test_question = "What are the contract terms?"
            result = await process_user_question(test_question)
            
            chunks = result.get('chunks', {})
            if chunks:
                print("✅ Elasticsearch integration working")
                print(f"Retrieved chunks: {chunks}")
                return True
            else:
                print("⚠️ No chunks retrieved from Elasticsearch")
                return False
                
        except Exception as e:
            print(f"❌ Elasticsearch integration failed: {e}")
            return False

    async def test_llm_response_format(self):
        """
        Test if LLM response is properly formatted
        """
        print(f"\n--- Testing LLM Response Format ---")
        
        try:
            test_question = "What type of document is this?"
            result = await process_user_question(test_question)
            
            # Check if result has expected structure
            required_keys = ['question', 'final_answer', 'chunks']
            missing_keys = [key for key in required_keys if key not in result]
            
            if not missing_keys:
                print("✅ LLM response format is correct")
                print(f"Response keys: {list(result.keys())}")
                return True
            else:
                print(f"❌ Missing keys in response: {missing_keys}")
                return False
                
        except Exception as e:
            print(f"❌ LLM response format test failed: {e}")
            return False

    async def test_edge_cases(self):
        """
        Test edge cases and error handling
        """
        print(f"\n--- Testing Edge Cases ---")
        
        edge_cases = [
            ("", "Empty question"),
            ("   ", "Whitespace only"),
            ("A" * 1000, "Very long question"),
            ("What?", "Very short question"),
            ("🤔 What are the terms? 📄", "Question with emojis"),
        ]
        
        results = {}
        
        for question, description in edge_cases:
            try:
                print(f"\nTesting: {description}")
                result = await process_user_question(question)
                results[description] = "✅ Handled gracefully"
                print(f"✅ {description}: Handled gracefully")
                
            except Exception as e:
                results[description] = f"❌ Error: {str(e)[:100]}"
                print(f"❌ {description}: {str(e)[:100]}")
        
        return results

    async def run_comprehensive_test(self):
        """
        Run a comprehensive test of the QA service
        """
        print("=" * 60)
        print("🧪 Starting QA Service Comprehensive Test")
        print("=" * 60)
        
        test_results = {}
        
        # Test 1: Valid questions
        print("\n📝 Testing Valid Questions")
        valid_results = []
        for question in self.test_questions[:3]:  # Test first 3 questions
            result = await self.test_valid_question(question)
            valid_results.append(result)
        
        test_results['valid_questions'] = all(valid_results)
        
        # Test 2: Invalid questions (guardrail testing)
        print("\n🛡️ Testing Invalid Questions (Guardrails)")
        invalid_results = []
        for question in self.invalid_questions[:2]:  # Test first 2 invalid questions
            result = await self.test_invalid_question(question)
            invalid_results.append(result)
        
        test_results['guardrails'] = all(invalid_results)
        
        # Test 3: Elasticsearch integration
        test_results['elasticsearch'] = await self.test_elasticsearch_integration()
        
        # Test 4: LLM response format
        test_results['llm_format'] = await self.test_llm_response_format()
        
        # Test 5: Edge cases
        edge_results = await self.test_edge_cases()
        test_results['edge_cases'] = len([r for r in edge_results.values() if r.startswith("✅")]) > 2
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 QA SERVICE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for test_name, passed in test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:20} | {status}")
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! QA Service is working correctly.")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ Most tests passed. Some issues need attention.")
        else:
            print("❌ Multiple failures detected. QA Service needs debugging.")
        
        print("=" * 60)

    async def test_single_question(self, question: str = None):
        """
        Test a single question for quick debugging
        """
        if not question:
            question = input("Enter a question to test: ")
        
        print(f"\n🔍 Testing Single Question")
        print(f"Question: {question}")
        print("-" * 40)
        
        try:
            result = await process_user_question(question)
            
            print("✅ SUCCESS!")
            print(f"Question: {result.get('question', 'N/A')}")
            print(f"Answer: {result.get('final_answer', 'N/A')}")
            
            chunks = result.get('chunks', {})
            if chunks and 'content' in chunks:
                print(f"Context chunks: {len(chunks['content'])}")
            
            return result
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            return None

    def run_manual_tests(self):
        """
        Run all manual tests - wrapper for async function
        """
        asyncio.run(self.run_comprehensive_test())

    def run_single_test(self, question: str = None):
        """
        Run single question test - wrapper for async function
        """
        asyncio.run(self.test_single_question(question))


# Helper functions for easy testing
def run_full_tests():
    """
    Run comprehensive QA service tests
    """
    test_instance = QAServiceTest()
    test_instance.run_manual_tests()


def test_question(question: str = None):
    """
    Test a single question
    """
    test_instance = QAServiceTest()
    test_instance.run_single_test(question)


if __name__ == "__main__":
    # You can run either comprehensive tests or single question test
    import sys
    
    if len(sys.argv) > 1:
        # If argument provided, test that specific question
        question = " ".join(sys.argv[1:])
        test_question(question)
    else:
        # Otherwise run comprehensive tests
        run_full_tests()
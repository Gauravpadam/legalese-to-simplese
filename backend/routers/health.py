from services.llm_service import ask_question
from fastapi import APIRouter, Depends
from services.health_service import get_health_status

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", summary="Health check", description="Returns OK if the service is alive")
async def health(status: dict = Depends(get_health_status)):
    return status

@router.get("/document-analysis")
async def get_document_analysis():
    """Return sample document analysis JSON"""
    return {
        "Document_Type": "Rental Agreement",
        "Main_Purpose": "To establish the terms and conditions for the rental of a residential property between a landlord and a tenant.",
        "Key_Highlights": [
            {
                "data": "11-month fixed term tenancy starting October 1, 2025."
            },
            {
                "data": "Monthly rent of ₹25,000 due by the 5th, with a steep ₹500/day late fee after 3 days."
            },
            {
                "data": "Refundable security deposit of ₹75,000, subject to deductions for unpaid rent, damages, or utilities."
            },
            {
                "data": "Either party can terminate with one-month written notice: early vacating without notice forfeits the deposit."
            }
        ],
        "Risk_Assessment": {
            "Risk_Score": 9,
            "High_Risk": [
                {
                    "title": "Steep Late Fee Penalty",
                    "description": "₹500/day late fee after 3 days is unusually high and may be unenforceable in court."
                },
                {
                    "title": "Deposit Forfeiture Clause",
                    "description": "Complete deposit forfeiture for early termination may be excessive and legally questionable."
                }
            ],
            "Medium_Risk": [
                {
                    "title": "Vague Maintenance Terms",
                    "description": "Minor repairs and major structural issues are not clearly defined."
                },
                {
                    "title": "Notice Period Ambiguity",
                    "description": "One-month notice requirement lacks specific delivery method requirements."
                }
            ]
        },
        "Key_Terms": [
            {
                "title": "Monthly Rent",
                "description": "₹25,000 Due by 5th of each month"
            },
            {
                "title": "Lease Duration",
                "description": "11 months Fixed term starting October 1, 2025"
            }
        ],
        "Suggested_Questions": [
            "What happens if I pay rent late?", 
            "Can I terminate the lease early?"
        ]
    }

@router.get("/test")
async def test_endpoint():
    return await ask_question(
        system_message="You are a helpful assistant that provides concise answers based on the user's input.",
        human_message="What is the capital of France?"
    )
    
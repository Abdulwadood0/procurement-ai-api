
# import asyncio

# from procurement_ai_api.agent.nodes import generate_query


# async def main():
#     result = await generate_query(
#         {
#             "question": (
#                 "Find purchases from OSHA Review Inc "
#                 "with a total price greater than 100"
#             )
#         }
#     )

#     print(result)


# if __name__ == "__main__":
#     asyncio.run(main())






# from procurement_ai_api.agent.validation import validate_query

# query = {
#     "supplier_name": "OSHA Review Inc",
#     "total_price": {"$gt": 100},
# }

# validate_query(query)
# print("Query is valid!")






# import asyncio

# from procurement_ai_api.agent.nodes import execute_query
# from procurement_ai_api.core.database import db_manager


# async def main():
#     await db_manager.connect()

#     try:
#         state = {
#             "query": {
#                 "supplier_name": "OSHA Review Inc",
#                 "total_price": {"$gt": 100},
#             }
#         }

#         result = await execute_query(state)
#         print(f"Found {len(result['results'])} documents")

#         for document in result["results"][:3]:
#             print(document)

#     finally:
#         await db_manager.close()


# if __name__ == "__main__":
#     asyncio.run(main())








# import asyncio

# from procurement_ai_api.agent.nodes import execute_query, generate_answer
# from procurement_ai_api.core.database import db_manager


# async def main():
#     await db_manager.connect()

#     try:
#         question = (
#             "Find purchases from OSHA Review Inc "
#             "with a total price greater than 100"
#         )

#         state = {
#             "question": question,
#             "query": {
#                 "supplier_name": "OSHA Review Inc",
#                 "total_price": {"$gt": 100},
#             },
#         }

#         state.update(await execute_query(state))
#         state.update(await generate_answer(state))

#         print(state["answer"])

#     finally:
#         await db_manager.close()


# if __name__ == "__main__":
#     asyncio.run(main())







# import asyncio

# from procurement_ai_api.agent.graph import graph
# from procurement_ai_api.core.database import db_manager


# async def main():
#     await db_manager.connect()

#     try:
#         result = await graph.ainvoke({
#             "question": (
#                         "Find purchases from OSHA Review Inc costing more than $100.",
#         "Which quarter had the highest total spending?",
#         "What are the 10 most frequently ordered items?",
#         "How many orders were created in 2014?",
#             )
#         })

#         print("Answer:")
#         print(result["answer"])

#     finally:
#         await db_manager.close()


# if __name__ == "__main__":
#     asyncio.run(main())




# import asyncio
# from langchain_openai import ChatOpenAI
# from procurement_ai_api.agent.schemas import QueryGeneration
# from procurement_ai_api.core.config import settings
# from procurement_ai_api.agent.prompts import MQL_SYSTEM_PROMPT


# async def main():
#     llm = ChatOpenAI(
#         model="gpt-4.1-mini",
#         api_key=settings.OPENAI_API_KEY,
#         temperature=0,
#     )

#     generator = llm.with_structured_output(
#         QueryGeneration,
#         method="function_calling",
#     )

#     result = await generator.ainvoke(
#     [
#         ("system", MQL_SYSTEM_PROMPT),
#         ("human", "Find purchases from OSHA Review Inc costing more than $100."),
#     ]
# )

#     print(result)


# if __name__ == "__main__":
#     asyncio.run(main())



# import asyncio
# from pprint import pprint

# from procurement_ai_api.agent.nodes import generate_query


# async def main():
#     questions = [
#         "Find purchases from OSHA Review Inc costing more than $100.",
#         "Which quarter had the highest total spending?",
#         "What are the 10 most frequently ordered items?",
#         "How many orders were created in 2014?",
#     ]

#     for question in questions:
#         print(f"\nQuestion: {question}")

#         result = await generate_query({"question": question})
#         pprint(result)


# if __name__ == "__main__":
#     asyncio.run(main())












# import asyncio
# from pprint import pprint

# from procurement_ai_api.agent.graph import graph
# from procurement_ai_api.core.database import db_manager


# QUESTIONS = [
#     # "give me the latest purchase from OSHA Review Inc costing more than $100.",
#     # "Which quarter had the highest total spending?",
#     # "What are the 10 most frequently ordered items?",
#     # "How many orders were created in 2014?",

#     "Which departments ordered from more than 5 distinct suppliers in 2014?"
# ]


# async def main():
#     await db_manager.connect()

#     try:
#         for question in QUESTIONS:
#             print("\n" + "=" * 80)
#             print(f"QUESTION: {question}")
#             print("=" * 80)

#             try:
#                 result = await graph.ainvoke(
#                 {
#         "question": question,
#     },
#     config={
#         "configurable": {
#             "thread_id": "debug-session"
#         }
#     }
# )

#                 print("\nGenerated query type:")
#                 print(result.get("query_type"))

#                 print("\nGenerated filter:")
#                 pprint(result.get("query", {}))

#                 print("\nGenerated pipeline:")
#                 pprint(result.get("pipeline", []))

#                 print("\nMongoDB results:")
#                 pprint(result.get("results", []))

#                 print("\nneeds_clarification:")
#                 pprint(result.get("needs_clarification", []))

#                 print("\nclarification_question:")
#                 pprint(result.get("clarification_question", []))

#                 print("\nFINAL ANSWER:")
#                 print(result.get("answer", "No answer generated."))

#             except Exception as e:
#                 print(f"\nFAILED: {type(e).__name__}: {e}")
#                 raise

#     finally:
#         await db_manager.close()


# if __name__ == "__main__":
#     asyncio.run(main())

import logging
import colorlog

handler = colorlog.StreamHandler()

handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.addHandler(handler)
logger.propagate = False

logger.debug("Debug message")
logger.info("Chat request succeeded")
logger.warning("Warning message")
logger.error("Chat request failed")
logger.critical("Critical error")
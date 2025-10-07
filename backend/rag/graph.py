"""
LangGraph workflow for agentic RAG system
Orchestrates multi-agent generation with sequential and parallel processing
"""

import asyncio
from typing import Dict, List, Any, TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from .agents import (
    AgentContext,
    ContentResearcher,
    CopywriterAgent,
    VisualDesignerAgent,
    VideoScriptwriterAgent,
    QualityAssuranceAgent
)

from .enhanced_vector_store import get_enhanced_vector_store

class GenerationState(TypedDict):
    """State structure for the generation workflow"""
    input: str
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    output_types: List[str]

    # Research phase
    research_context: List[str]
    research_summary: str

    # Generation phase
    generated_text: str
    poster_prompt: str
    video_script: str

    # Agent notes
    copywriter_notes: str
    visual_designer_notes: str
    video_scriptwriter_notes: str

    # Quality assurance
    quality_scores: Dict[str, float]
    validation_feedback: Dict[str, str]
    qa_notes: str

    # Final outputs
    final_text: str
    final_poster_prompt: str
    final_video_script: str

    # Error handling
    errors: List[str]
    retry_count: int

class GenerationGraph:
    """Main orchestration graph for multi-agent generation"""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create the main generation graph"""

        # Initialize the graph
        workflow = StateGraph(GenerationState)

        # Add nodes (agents)
        workflow.add_node("research", self._research_node)
        workflow.add_node("text_generation", self._text_generation_node)
        workflow.add_node("poster_generation", self._poster_generation_node)
        workflow.add_node("video_generation", self._video_generation_node)
        workflow.add_node("quality_assurance", self._quality_assurance_node)
        workflow.add_node("refinement", self._refinement_node)
        workflow.add_node("error_handler", self._error_handler_node)

        # Define the flow - Sequential instead of parallel to avoid concurrent updates
        workflow.set_entry_point("research")

        # Research -> Text generation -> Poster generation -> Video generation -> Quality assurance
        workflow.add_edge("research", "text_generation")
        workflow.add_edge("text_generation", "poster_generation")
        workflow.add_edge("poster_generation", "video_generation")
        workflow.add_edge("video_generation", "quality_assurance")

        # Quality assurance -> refinement (if needed)
        workflow.add_conditional_edges(
            "quality_assurance",
            self._should_refine,
            {
                "refine": "refinement",
                "complete": END
            }
        )

        # Refinement can go back to quality assurance or complete
        workflow.add_conditional_edges(
            "refinement",
            self._should_continue_refinement,
            {
                "continue": "quality_assurance",
                "complete": END
            }
        )

        # Remove problematic error handling edges that can cause concurrent updates
        # workflow.add_edge("research", "error_handler")
        # workflow.add_edge("text_generation", "error_handler")
        # workflow.add_edge("poster_generation", "error_handler")
        # workflow.add_edge("video_generation", "error_handler")
        # workflow.add_edge("quality_assurance", "error_handler")

        return workflow.compile()

    def _research_node(self, state: GenerationState) -> GenerationState:
        """Execute content research"""
        try:
            # Initialize vector store and embedding model
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            # Create agent context
            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,  # Pass the actual vector store, not the enhanced one
                embedding_model=embedding_model
            )

            researcher = ContentResearcher(context)
            new_state = asyncio.run(researcher.execute(state))

            return new_state

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Research error: {str(e)}"]
            }

    def _text_generation_node(self, state: GenerationState) -> GenerationState:
        """Execute text generation"""
        try:
            # Initialize vector store and embedding model
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,  # Pass the actual vector store, not the enhanced one
                embedding_model=embedding_model
            )

            copywriter = CopywriterAgent(context)
            new_state = asyncio.run(copywriter.execute(state))

            return new_state

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Text generation error: {str(e)}"]
            }

    def _poster_generation_node(self, state: GenerationState) -> GenerationState:
        """Execute poster generation"""
        try:
            # Initialize vector store and embedding model
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,  # Pass the actual vector store, not the enhanced one
                embedding_model=embedding_model
            )

            designer = VisualDesignerAgent(context)
            new_state = asyncio.run(designer.execute(state))

            return new_state

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Poster generation error: {str(e)}"]
            }

    def _video_generation_node(self, state: GenerationState) -> GenerationState:
        """Execute video generation"""
        try:
            # Initialize vector store and embedding model
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,  # Pass the actual vector store, not the enhanced one
                embedding_model=embedding_model
            )

            scriptwriter = VideoScriptwriterAgent(context)
            new_state = asyncio.run(scriptwriter.execute(state))

            return new_state

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Video generation error: {str(e)}"]
            }

    def _quality_assurance_node(self, state: GenerationState) -> GenerationState:
        """Execute quality assurance"""
        try:
            # Initialize vector store and embedding model
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,  # Pass the actual vector store, not the enhanced one
                embedding_model=embedding_model
            )

            qa_agent = QualityAssuranceAgent(context)
            new_state = asyncio.run(qa_agent.execute(state))

            return new_state

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"QA error: {str(e)}"]
            }

    def _refinement_node(self, state: GenerationState) -> GenerationState:
        """Refine outputs based on QA feedback"""
        try:
            # Simple refinement logic - in production, this would use the LLM again
            # For now, we'll just mark the current outputs as final

            quality_scores = state.get("quality_scores", {})
            overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 5.0

            # If quality is good enough, mark as final
            if overall_score >= 7.0:
                return {
                    **state,
                    "final_text": state.get("generated_text", ""),
                    "final_poster_prompt": state.get("poster_prompt", ""),
                    "final_video_script": state.get("video_script", "")
                }
            else:
                # Mark for further refinement
                return {
                    **state,
                    "retry_count": state.get("retry_count", 0) + 1
                }

        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Refinement error: {str(e)}"]
            }

    def _error_handler_node(self, state: GenerationState) -> GenerationState:
        """Handle errors and provide fallbacks"""
        errors = state.get("errors", [])

        if errors:
            # Log errors and provide fallback content
            print(f"Generation errors: {errors}")

            # Provide basic fallback content
            fallback_state = {
                **state,
                "generated_text": f"Generated content for {state['platform']} - {state['input']}",
                "poster_prompt": f"Create a {state['tone']} poster for {state['platform']} featuring: {state['input']}",
                "video_script": f"SCENE 1: Show product/service\nNARRATION: {state['input']}\n\nSCENE 2: Call to action\nNARRATION: Visit us today!",
                "errors": errors
            }

            return fallback_state

        return state

    def _should_refine(self, state: GenerationState) -> str:
        """Determine if refinement is needed"""
        quality_scores = state.get("quality_scores", {})
        if not quality_scores:
            return "complete"

        overall_score = sum(quality_scores.values()) / len(quality_scores)

        # Refine if quality is below threshold or retry count is low
        if overall_score < 7.0 and state.get("retry_count", 0) < 2:
            return "refine"
        else:
            return "complete"

    def _should_continue_refinement(self, state: GenerationState) -> str:
        """Determine if refinement should continue"""
        retry_count = state.get("retry_count", 0)

        # Stop refinement after 2 attempts
        if retry_count >= 2:
            return "complete"
        else:
            return "continue"

    async def run(self, initial_state: GenerationState) -> GenerationState:
        """Run the complete generation workflow"""
        try:
            # Ensure all required state keys are initialized
            complete_state = {
                "input": initial_state.get("input", ""),
                "platform": initial_state.get("platform", ""),
                "tone": initial_state.get("tone", ""),
                "brand_guidelines": initial_state.get("brand_guidelines"),
                "output_types": initial_state.get("output_types", []),
                "research_context": initial_state.get("research_context", []),
                "research_summary": initial_state.get("research_summary", ""),
                "generated_text": initial_state.get("generated_text", ""),
                "poster_prompt": initial_state.get("poster_prompt", ""),
                "video_script": initial_state.get("video_script", ""),
                "copywriter_notes": initial_state.get("copywriter_notes", ""),
                "visual_designer_notes": initial_state.get("visual_designer_notes", ""),
                "video_scriptwriter_notes": initial_state.get("video_scriptwriter_notes", ""),
                "quality_scores": initial_state.get("quality_scores", {}),
                "validation_feedback": initial_state.get("validation_feedback", {}),
                "qa_notes": initial_state.get("qa_notes", ""),
                "final_text": initial_state.get("final_text", ""),
                "final_poster_prompt": initial_state.get("final_poster_prompt", ""),
                "final_video_script": initial_state.get("final_video_script", ""),
                "errors": initial_state.get("errors", []),
                "retry_count": initial_state.get("retry_count", 0)
            }

            result = await self.graph.ainvoke(complete_state)
            return result
        except Exception as e:
            # Return state with error information
            return {
                **initial_state,
                "errors": initial_state.get("errors", []) + [f"Workflow error: {str(e)}"],
                "generated_text": f"Error in generation: {str(e)}"
            }

def create_generation_graph(model_name: str = "microsoft/DialoGPT-medium") -> GenerationGraph:
    """Factory function to create generation graph"""
    return GenerationGraph(model_name)

# Convenience function for running the workflow
async def run_generation_workflow(
    input_text: str,
    platform: str,
    tone: str,
    output_types: List[str],
    brand_guidelines: Optional[str] = None,
    model_name: str = "microsoft/DialoGPT-medium"
) -> Dict[str, Any]:
    """Run the complete generation workflow"""

    # Initialize state
    initial_state: GenerationState = {
        "input": input_text,
        "platform": platform,
        "tone": tone,
        "brand_guidelines": brand_guidelines,
        "output_types": output_types,
        "research_context": [],
        "research_summary": "",
        "generated_text": "",
        "poster_prompt": "",
        "video_script": "",
        "copywriter_notes": "",
        "visual_designer_notes": "",
        "video_scriptwriter_notes": "",
        "quality_scores": {},
        "validation_feedback": {},
        "qa_notes": "",
        "final_text": "",
        "final_poster_prompt": "",
        "final_video_script": "",
        "errors": [],
        "retry_count": 0
    }

    # Create and run the graph
    graph = create_generation_graph(model_name)
    result = await graph.run(initial_state)

    # Extract final outputs
    return {
        "text": result.get("final_text", result.get("generated_text", "")),
        "poster_prompt": result.get("final_poster_prompt", result.get("poster_prompt", "")),
        "video_script": result.get("final_video_script", result.get("video_script", "")),
        "quality_scores": result.get("quality_scores", {}),
        "validation_feedback": result.get("validation_feedback", {}),
        "errors": result.get("errors", [])
    }

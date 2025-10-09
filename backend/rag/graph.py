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
    QualityAssuranceAgent,
    LogoIntegrationAgent,
    PosterFinalizationAgent
)

from .enhanced_vector_store import get_enhanced_vector_store

class GenerationState(TypedDict):
    """State structure for the generation workflow"""
    input: str
    platform: str
    tone: str
    brand_guidelines: Optional[str]
    output_types: List[str]

    # Logo integration
    logo_data: Optional[bytes]
    logo_position: str
    logo_file: Optional[Any]
    logo_processed: bool
    logo_id: Optional[str]
    logo_path: Optional[str]
    logo_filename: Optional[str]
    logo_size: Optional[int]
    logo_integration_notes: Optional[str]
    logo_error: Optional[str]
    poster_finalized: bool
    finalization_notes: Optional[str]

    # Research phase
    research_context: List[str]
    research_summary: str

    # Generation phase
    generated_text: str
    poster_prompt: str
    poster_url: Optional[str]
    poster_file_path: Optional[str]
    poster_filename: Optional[str]
    poster_generation_notes: Optional[str]
    poster_error: Optional[str]
    video_script: str
    video_gif_url: Optional[str]
    video_gif_file_path: Optional[str]
    video_gif_filename: Optional[str]
    video_generation_notes: Optional[str]
    video_error: Optional[str]
    video_frame_prompts: Optional[List[str]]

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

    # Feedback insights
    feedback_summary: Optional[str]
    feedback_highlights: List[str]
    feedback_suggestions: List[str]
    feedback_keywords: List[str]
    feedback_avg_rating: Optional[float]

    # Error handling
    errors: List[str]
    retry_count: int

class GenerationGraph:
    """Main orchestration graph for multi-agent generation"""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.vector_store = get_enhanced_vector_store()
        self.embedding_model = self.vector_store.embedding_model
        self.graph = self._create_graph()
        
    def _get_agent_context(self, state: GenerationState) -> AgentContext:
        """Create a consistent agent context from the current state"""
        return AgentContext(
            platform=state["platform"],
            tone=state["tone"],
            brand_guidelines=state.get("brand_guidelines"),
            input_text=state["input"],
            vector_store=self.vector_store.vector_store,
            embedding_model=self.embedding_model,
            feedback_summary=state.get("feedback_summary"),
            feedback_highlights=state.get("feedback_highlights"),
            feedback_suggestions=state.get("feedback_suggestions"),
            feedback_keywords=state.get("feedback_keywords"),
            feedback_avg_rating=state.get("feedback_avg_rating"),
            logo_data=state.get("logo_data"),
            logo_position=state.get("logo_position", "top-right")
        )

    def _create_graph(self) -> StateGraph:
        """Create the main generation graph"""
        workflow = StateGraph(GenerationState)

        # Add nodes (agents)
        workflow.add_node("research", self._research_node)
        workflow.add_node("text_generation", self._text_generation_node)
        workflow.add_node("logo_integration", self._logo_integration_node)
        workflow.add_node("poster_generation", self._poster_generation_node)
        workflow.add_node("poster_finalization", self._poster_finalization_node)
        workflow.add_node("video_generation", self._video_generation_node)
        workflow.add_node("quality_assurance", self._quality_assurance_node)
        workflow.add_node("refinement", self._refinement_node)

        # Define the flow - Sequential
        workflow.set_entry_point("research")
        workflow.add_edge("research", "text_generation")
        workflow.add_edge("text_generation", "logo_integration")
        workflow.add_edge("logo_integration", "poster_generation")
        workflow.add_edge("poster_generation", "poster_finalization")
        workflow.add_edge("poster_finalization", "video_generation")
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

        return workflow.compile()

    def _research_node(self, state: GenerationState) -> GenerationState:
        """Execute content research"""
        try:
            context = self._get_agent_context(state)
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
            context = self._get_agent_context(state)
            copywriter = CopywriterAgent(context)
            new_state = asyncio.run(copywriter.execute(state))
            return new_state
        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Text generation error: {str(e)}"]
            }

    def _logo_integration_node(self, state: GenerationState) -> GenerationState:
        """Execute logo integration"""
        try:
            print("🎨 Logo Integration Node: Starting logo processing...")
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,
                embedding_model=embedding_model,
                logo_data=state.get("logo_data"),
                logo_position=state.get("logo_position", "top-right")
            )

            logo_agent = LogoIntegrationAgent(context)
            new_state = asyncio.run(logo_agent.execute(state))

            print(f"🎨 Logo Integration Node: Completed. Logo processed: {new_state.get('logo_processed', False)}")
            return new_state
        except Exception as e:
            print(f"❌ Logo Integration Node: Error - {str(e)}")
            return {
                **state,
                "errors": state.get("errors", []) + [f"Logo integration error: {str(e)}"],
                "logo_processed": False,
                "logo_error": str(e)
            }

    def _poster_generation_node(self, state: GenerationState) -> GenerationState:
        """Execute poster generation"""
        try:
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,
                embedding_model=embedding_model,
                feedback_summary=state.get("feedback_summary"),
                feedback_highlights=state.get("feedback_highlights"),
                feedback_suggestions=state.get("feedback_suggestions"),
                feedback_keywords=state.get("feedback_keywords"),
                feedback_avg_rating=state.get("feedback_avg_rating"),
                logo_data=state.get("logo_data"),
                logo_position=state.get("logo_position", "top-right")
            )

            designer = VisualDesignerAgent(context)
            new_state = asyncio.run(designer.execute(state))
            return new_state
        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Poster generation error: {str(e)}"]
            }

    def _poster_finalization_node(self, state: GenerationState) -> GenerationState:
        """Execute poster finalization"""
        try:
            print("🎨 Poster Finalization Node: Starting poster finalization...")
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,
                embedding_model=embedding_model,
                logo_data=state.get("logo_data"),
                logo_position=state.get("logo_position", "top-right")
            )

            finalization_agent = PosterFinalizationAgent(context)
            new_state = asyncio.run(finalization_agent.execute(state))

            print(f"🎨 Poster Finalization Node: Completed. Finalized: {new_state.get('poster_finalized', False)}")
            return new_state
        except Exception as e:
            print(f"❌ Poster Finalization Node: Error - {str(e)}")
            return {
                **state,
                "errors": state.get("errors", []) + [f"Poster finalization error: {str(e)}"],
                "poster_finalized": False,
                "finalization_notes": str(e)
            }

    def _video_generation_node(self, state: GenerationState) -> GenerationState:
        """Execute video generation - now generates actual video GIF"""
        try:
            print("🎬 Video Generation Node: Starting video generation...")
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,
                embedding_model=embedding_model,
                feedback_summary=state.get("feedback_summary"),
                feedback_highlights=state.get("feedback_highlights"),
                feedback_suggestions=state.get("feedback_suggestions"),
                feedback_keywords=state.get("feedback_keywords"),
                feedback_avg_rating=state.get("feedback_avg_rating"),
                logo_data=state.get("logo_data"),
                logo_position=state.get("logo_position", "top-right")
            )

            scriptwriter = VideoScriptwriterAgent(context)
            new_state = asyncio.run(scriptwriter.execute(state))

            print(f"🎬 Video Generation Node: Completed. Video URL: {new_state.get('video_gif_url', 'None')[:50]}...")
            return new_state
        except Exception as e:
            print(f"❌ Video Generation Node: Error - {str(e)}")
            return {
                **state,
                "errors": state.get("errors", []) + [f"Video generation error: {str(e)}"],
                "video_error": str(e)
            }

    def _quality_assurance_node(self, state: GenerationState) -> GenerationState:
        """Execute quality assurance"""
        print(f"QA Node: Processing state with generated_text: '{state.get('generated_text', '')[:50]}...'")
        try:
            vector_store = get_enhanced_vector_store()
            embedding_model = vector_store.embedding_model

            context = AgentContext(
                platform=state["platform"],
                tone=state["tone"],
                brand_guidelines=state.get("brand_guidelines"),
                input_text=state["input"],
                vector_store=vector_store.vector_store,
                embedding_model=embedding_model
            )

            qa_agent = QualityAssuranceAgent(context)
            new_state = asyncio.run(qa_agent.execute(state))

            print(f"QA Node: Completed. Final text set to: '{new_state.get('final_text', '')[:50]}...'")
            return new_state
        except Exception as e:
            print(f"QA Node: Error - {str(e)}")
            return {
                **state,
                "errors": state.get("errors", []) + [f"QA error: {str(e)}"]
            }

    def _refinement_node(self, state: GenerationState) -> GenerationState:
        """Refine outputs based on QA feedback"""
        try:
            quality_scores = state.get("quality_scores", {})
            overall_score = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 5.0

            if overall_score >= 7.0:
                return {
                    **state,
                    "final_text": state.get("generated_text", ""),
                    "final_poster_prompt": state.get("poster_prompt", ""),
                    "final_video_script": state.get("video_script", "")
                }
            else:
                return {
                    **state,
                    "retry_count": state.get("retry_count", 0) + 1
                }
        except Exception as e:
            return {
                **state,
                "errors": state.get("errors", []) + [f"Refinement error: {str(e)}"]
            }

    def _should_refine(self, state: GenerationState) -> str:
        """Determine if refinement is needed"""
        quality_scores = state.get("quality_scores", {})
        if not quality_scores:
            return "complete"

        overall_score = sum(quality_scores.values()) / len(quality_scores)

        if overall_score < 7.0 and state.get("retry_count", 0) < 2:
            return "refine"
        else:
            return "complete"

    def _should_continue_refinement(self, state: GenerationState) -> str:
        """Determine if refinement should continue"""
        retry_count = state.get("retry_count", 0)
        if retry_count >= 2:
            return "complete"
        else:
            return "continue"

    async def run(self, initial_state: GenerationState) -> GenerationState:
        """Run the complete generation workflow"""
        try:
            complete_state = {
                "input": initial_state.get("input", ""),
                "platform": initial_state.get("platform", ""),
                "tone": initial_state.get("tone", ""),
                "brand_guidelines": initial_state.get("brand_guidelines"),
                "output_types": initial_state.get("output_types", []),
                "logo_data": initial_state.get("logo_data"),
                "logo_position": initial_state.get("logo_position", "top-right"),
                "logo_file": initial_state.get("logo_file"),
                "logo_processed": initial_state.get("logo_processed", False),
                "logo_id": initial_state.get("logo_id"),
                "logo_path": initial_state.get("logo_path"),
                "logo_filename": initial_state.get("logo_filename"),
                "logo_size": initial_state.get("logo_size"),
                "logo_integration_notes": initial_state.get("logo_integration_notes"),
                "logo_error": initial_state.get("logo_error"),
                "poster_finalized": initial_state.get("poster_finalized", False),
                "finalization_notes": initial_state.get("finalization_notes"),
                "research_context": initial_state.get("research_context", []),
                "research_summary": initial_state.get("research_summary", ""),
                "generated_text": initial_state.get("generated_text", ""),
                "poster_prompt": initial_state.get("poster_prompt", ""),
                "poster_url": initial_state.get("poster_url"),
                "poster_file_path": initial_state.get("poster_file_path"),
                "poster_filename": initial_state.get("poster_filename"),
                "poster_generation_notes": initial_state.get("poster_generation_notes"),
                "poster_error": initial_state.get("poster_error"),
                "video_script": initial_state.get("video_script", ""),
                "video_gif_url": initial_state.get("video_gif_url"),
                "video_gif_file_path": initial_state.get("video_gif_file_path"),
                "video_gif_filename": initial_state.get("video_gif_filename"),
                "video_generation_notes": initial_state.get("video_generation_notes"),
                "video_error": initial_state.get("video_error"),
                "video_frame_prompts": initial_state.get("video_frame_prompts"),
                "copywriter_notes": initial_state.get("copywriter_notes", ""),
                "visual_designer_notes": initial_state.get("visual_designer_notes", ""),
                "video_scriptwriter_notes": initial_state.get("video_scriptwriter_notes", ""),
                "quality_scores": initial_state.get("quality_scores", {}),
                "validation_feedback": initial_state.get("validation_feedback", {}),
                "qa_notes": initial_state.get("qa_notes", ""),
                "final_text": initial_state.get("final_text", ""),
                "final_poster_prompt": initial_state.get("final_poster_prompt", ""),
                "final_video_script": initial_state.get("final_video_script", ""),
                "feedback_summary": initial_state.get("feedback_summary"),
                "feedback_highlights": initial_state.get("feedback_highlights", []),
                "feedback_suggestions": initial_state.get("feedback_suggestions", []),
                "feedback_keywords": initial_state.get("feedback_keywords", []),
                "feedback_avg_rating": initial_state.get("feedback_avg_rating"),
                "errors": initial_state.get("errors", []),
                "retry_count": initial_state.get("retry_count", 0)
            }

            result = await self.graph.ainvoke(complete_state)
            return result
        except Exception as e:
            return {
                **initial_state,
                "errors": initial_state.get("errors", []) + [f"Workflow error: {str(e)}"],
                "generated_text": f"Error in generation: {str(e)}"
            }

def create_generation_graph(model_name: str = "microsoft/DialoGPT-medium") -> GenerationGraph:
    """Factory function to create generation graph"""
    return GenerationGraph(model_name)

async def run_generation_workflow(
    input_text: str,
    platform: str,
    tone: str,
    output_types: List[str],
    brand_guidelines: Optional[str] = None,
    feedback_insights: Optional[Dict[str, Any]] = None,
    model_name: str = "microsoft/DialoGPT-medium",
    logo_data: Optional[bytes] = None,
    logo_file: Optional[Any] = None,
    logo_position: str = "top-right"
) -> Dict[str, Any]:
    """Run the complete generation workflow"""

    feedback_summary = None
    feedback_highlights: List[str] = []
    feedback_suggestions: List[str] = []
    feedback_keywords: List[str] = []
    feedback_avg_rating: Optional[float] = None

    if feedback_insights:
        feedback_summary = feedback_insights.get("summary")
        raw_highlights = feedback_insights.get("positive_highlights") or []
        raw_suggestions = feedback_insights.get("improvement_suggestions") or []
        raw_keywords = feedback_insights.get("common_keywords") or []
        feedback_highlights = [str(item) for item in raw_highlights if item]
        feedback_suggestions = [str(item) for item in raw_suggestions if item]
        feedback_keywords = [str(item) for item in raw_keywords if item]
        avg_rating = feedback_insights.get("avg_rating")
        feedback_avg_rating = float(avg_rating) if avg_rating is not None else None

    # Initialize state
    initial_state: GenerationState = {
        "input": input_text,
        "platform": platform,
        "tone": tone,
        "brand_guidelines": brand_guidelines,
        "output_types": output_types,
        "logo_data": logo_data,
        "logo_position": logo_position,
        "logo_file": logo_file,
        "logo_processed": False,
        "logo_id": None,
        "logo_path": None,
        "logo_filename": None,
        "logo_size": None,
        "logo_integration_notes": None,
        "logo_error": None,
        "poster_finalized": False,
        "finalization_notes": None,
        "research_context": [],
        "research_summary": "",
        "generated_text": "",
        "poster_prompt": "",
        "poster_url": None,
        "poster_file_path": None,
        "poster_filename": None,
        "poster_generation_notes": None,
        "poster_error": None,
        "video_script": "",
        "video_gif_url": None,
        "video_gif_file_path": None,
        "video_gif_filename": None,
        "video_generation_notes": None,
        "video_error": None,
        "video_frame_prompts": None,
        "copywriter_notes": "",
        "visual_designer_notes": "",
        "video_scriptwriter_notes": "",
        "quality_scores": {},
        "validation_feedback": {},
        "qa_notes": "",
        "final_text": "",
        "final_poster_prompt": "",
        "final_video_script": "",
        "feedback_summary": feedback_summary,
        "feedback_highlights": feedback_highlights,
        "feedback_suggestions": feedback_suggestions,
        "feedback_keywords": feedback_keywords,
        "feedback_avg_rating": feedback_avg_rating,
        "errors": [],
        "retry_count": 0
    }

    # Create and run the graph
    graph = create_generation_graph(model_name)
    result = await graph.run(initial_state)

    # Extract final outputs
    final_text = result.get("final_text", result.get("generated_text", ""))
    final_poster = result.get("final_poster_prompt", result.get("poster_prompt", ""))
    final_video = result.get("final_video_script", result.get("video_script", ""))
    final_poster_url = result.get("poster_url")
    final_video_gif_url = result.get("video_gif_url")

    # Print completion summary
    output_types = result.get("output_types", [])
    completion_parts = []
    
    if "text" in output_types:
        completion_parts.append(f"Text: '{final_text[:50]}...'")
    
    if "poster" in output_types:
        if final_poster_url:
            completion_parts.append("Poster: Generated successfully")
        else:
            completion_parts.append("Poster: Failed")
    
    if "video" in output_types:
        if final_video_gif_url:
            completion_parts.append("Video GIF: Generated successfully")
        else:
            completion_parts.append(f"Video Script: '{final_video[:30]}...'")
    
    print(f"Workflow completed. {', '.join(completion_parts)}")

    return {
        "text": final_text,
        "poster_prompt": final_poster,
        "poster_url": final_poster_url,
        "video_script": final_video,
        "video_gif_url": final_video_gif_url,
        "video_gif_file_path": result.get("video_gif_file_path"),
        "video_gif_filename": result.get("video_gif_filename"),
        "video_frame_prompts": result.get("video_frame_prompts"),
        "quality_scores": result.get("quality_scores", {}),
        "validation_feedback": result.get("validation_feedback", {}),
        "errors": result.get("errors", [])
    }
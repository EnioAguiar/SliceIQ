import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from models.highlight import ScoredHighlight
from models.profile import Profile

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    INITIAL = "initial"
    ANALYZED = "analyzed"
    CANDIDATES_GENERATED = "candidates_generated"
    SCORED = "scored"
    SELECTED = "selected"
    VALIDATED = "validated"
    COMPLETE = "complete"


class WorkflowError(Exception):
    pass


class VideoClippingWorkflow:
    def __init__(self, video_path: str, profile: Profile, analyzer):
        self.video_path = video_path
        self.profile = profile
        self.analyzer = analyzer
        self.workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._state = {
            "stage": WorkflowStage.INITIAL.value,
            "video_path": video_path,
            "profile_name": profile.name,
            "candidates": [],
            "scored_candidates": [],
            "selected_highlights": [],
            "error": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._workflow_dir = Path(f".planning/workflows/{self.workflow_id}")
        self._workflow_dir.mkdir(parents=True, exist_ok=True)

    @property
    def stage(self) -> WorkflowStage:
        return WorkflowStage(self._state["stage"])

    @property
    def candidates(self) -> list[dict]:
        return self._state["candidates"]

    @property
    def scored_candidates(self) -> list[ScoredHighlight]:
        return self._state["scored_candidates"]

    @property
    def selected_highlights(self) -> list[dict]:
        return self._state["selected_highlights"]

    def save_state(self):
        self._state["updated_at"] = datetime.now().isoformat()
        state_file = self._workflow_dir / "state.json"
        with open(state_file, "w") as f:
            json.dump(self._state, f, indent=2, default=str)
        logger.info(f"Workflow state saved to {state_file}")

    def load_state(self, workflow_id: str) -> bool:
        state_file = Path(f".planning/workflows/{workflow_id}/state.json")
        if not state_file.exists():
            return False
        with open(state_file) as f:
            data = json.load(f)
        self.workflow_id = workflow_id
        self._workflow_dir = Path(f".planning/workflows/{workflow_id}")
        self._state = data
        return True

    def execute_stage(self, target_stage: WorkflowStage) -> dict:
        stage_order = [
            WorkflowStage.INITIAL,
            WorkflowStage.ANALYZED,
            WorkflowStage.CANDIDATES_GENERATED,
            WorkflowStage.SCORED,
            WorkflowStage.SELECTED,
            WorkflowStage.VALIDATED,
            WorkflowStage.COMPLETE,
        ]
        current_idx = stage_order.index(self.stage)
        target_idx = stage_order.index(target_stage)

        if target_idx <= current_idx:
            raise WorkflowError(
                f"Cannot go back from {self.stage.value} to {target_stage.value}"
            )

        for stage in stage_order[current_idx + 1 : target_idx + 1]:
            self._execute_single_stage(stage)
            self.save_state()

        return self._state

    def _execute_single_stage(self, stage: WorkflowStage):
        logger.info(f"Executing stage: {stage.value}")
        if stage == WorkflowStage.ANALYZED:
            self._stage_analyze()
        elif stage == WorkflowStage.CANDIDATES_GENERATED:
            self._stage_generate_candidates()
        elif stage == WorkflowStage.SCORED:
            self._stage_score()
        elif stage == WorkflowStage.SELECTED:
            self._stage_select()
        elif stage == WorkflowStage.VALIDATED:
            self._stage_validate()
        elif stage == WorkflowStage.COMPLETE:
            self._stage_complete()

    def _stage_analyze(self):
        transcript_file = Path("transcript_debug.json")
        if transcript_file.exists():
            with open(transcript_file) as f:
                data = json.load(f)
            self._state["transcript_segments"] = data.get("segments", [])
            self._state["has_transcript"] = True
        else:
            self._state["transcript_segments"] = []
            self._state["has_transcript"] = False
        self._state["stage"] = WorkflowStage.ANALYZED.value

    def _stage_generate_candidates(self):
        if not self._state.get("has_transcript"):
            raise WorkflowError("Cannot generate candidates without transcript. Run ANALYZE first.")

        segments = self._state.get("transcript_segments", [])
        if not segments:
            raise WorkflowError("Transcript has no segments.")

        segments_text = "\n".join([
            f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}"
            for s in segments
        ])

        num_candidates = self.profile.quantity * 3

        prompt = f"""Analise o transcript e identifique {num_candidates} momentos potenciais para highlights.

REGRAS OBRIGATÓRIAS:
- Cada highlight deve ter entre {self.profile.duration_min}s e {self.profile.duration_max}s
- Timestamps devem ser momentos distintos, não consecutivos
- Priorizar momentos com hook forte (pergunta, declaração impactante)
- Priorizar momentos com alto potencial viral (engagement drivers)
- Timestamps devem ser em SEGUNDOS EXATOS (ex: 125.5, não 2:05)

Transcript:
{segments_text}

Retorne {num_candidates} candidatos em formato JSON:
{{"candidates": [
  {{"start": float, "end": float, "score": int, "reason": str}}
]}}"""

        response = self.analyzer._call_llm(prompt, num_candidates)
        candidates = self.analyzer._parse_response(response)

        self._state["candidates"] = [
            {"start": c.start, "end": c.end, "score": c.score, "reason": c.reason}
            for c in candidates
        ]
        self._state["stage"] = WorkflowStage.CANDIDATES_GENERATED.value

        candidates_file = self._workflow_dir / "candidates.json"
        with open(candidates_file, "w") as f:
            json.dump(self._state["candidates"], f, indent=2)

    def _stage_score(self):
        if not self._state.get("candidates"):
            raise WorkflowError("No candidates to score. Run GENERATE_CANDIDATES first.")

        candidates_list = "\n".join([
            f"- start={c['start']:.1f}s, end={c['end']:.1f}s, score={c['score']}, reason={c['reason']}"
            for c in self._state["candidates"]
        ])

        prompt = f"""Avalie cada candidato quanto a:
1. HOOK_SCORE (0-100): Quão forte é o início? Captura atenção imediatamente?
2. VIRAL_SCORE (0-100): Potencial para viralizar/engajar? Contém citação marcante, número impactante, ou polêmica?
3. DURATION_SCORE (0-100): Comply com {self.profile.duration_min}-{self.profile.duration_max}s range?

Duração desejada: target={self.profile.duration_min}s, min={self.profile.duration_min}s, max={self.profile.duration_max}s

Candidatos:
{candidates_list}

Retorne JSON com scores para cada candidato:
{{"scored": [
  {{"start": float, "end": float, "hook_score": int, "viral_score": int, "duration_score": int}}
]}}"""

        response = self.analyzer._call_llm(prompt, self.profile.quantity)
        scored = self._parse_scored_response(response)

        self._state["scored_candidates"] = [s.model_dump() for s in scored]
        self._state["stage"] = WorkflowStage.SCORED.value

        scored_file = self._workflow_dir / "scored.json"
        with open(scored_file, "w") as f:
            json.dump(self._state["scored_candidates"], f, indent=2)

    def _parse_scored_response(self, response: str) -> list[ScoredHighlight]:
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group())
        scored_list = []

        for item in data.get("scored", []):
            hook = item.get("hook_score", 50)
            viral = item.get("viral_score", 50)
            duration = item.get("duration_score", 50)
            total = int(hook * 0.4 + viral * 0.3 + duration * 0.3)

            scored_list.append(ScoredHighlight(
                start=item["start"],
                end=item["end"],
                score=item.get("score", 50),
                reason=item.get("reason", ""),
                hook_score=hook,
                viral_score=viral,
                duration_score=duration,
                total_score=total,
                rank=0,
            ))

        return scored_list

    def _stage_select(self):
        scored = self._state.get("scored_candidates", [])
        if not scored:
            raise WorkflowError("No scored candidates. Run SCORE first.")

        scored.sort(key=lambda x: x.get("total_score", 0), reverse=True)

        selected = []
        used_ranges = []
        min_gap = 5.0

        for item in scored:
            if len(selected) >= self.profile.quantity:
                break

            start = item["start"]
            end = item["end"]
            overlaps = False
            for used_start, used_end in used_ranges:
                if not (end + min_gap < used_start or start - min_gap > used_end):
                    overlaps = True
                    break

            if not overlaps:
                item["rank"] = len(selected) + 1
                selected.append(item)
                used_ranges.append((start, end))

        self._state["selected_highlights"] = selected
        self._state["stage"] = WorkflowStage.SELECTED.value

        selected_file = self._workflow_dir / "selected.json"
        with open(selected_file, "w") as f:
            json.dump(self._state["selected_highlights"], f, indent=2)

    def _stage_validate(self):
        selected = self._state.get("selected_highlights", [])
        if not selected:
            raise WorkflowError("No selected highlights. Run SELECT first.")

        validated = []
        re_evaluated = []

        for item in selected:
            duration = item["end"] - item["start"]
            min_dur = self.profile.duration_min
            max_dur = self.profile.duration_max

            if duration < min_dur:
                extension = min_dur - duration
                extension_pct = (extension / duration) * 100 if duration > 0 else 100
                if extension_pct > 30:
                    re_evaluated.append(item)
                    continue
                item["end"] = item["start"] + min_dur
            elif duration > max_dur:
                item["end"] = item["start"] + max_dur

            if item.get("total_score", 0) < self.profile.score_minimum:
                continue

            validated.append(item)

        self._state["validated_highlights"] = validated
        self._state["re_evaluated"] = re_evaluated
        self._state["stage"] = WorkflowStage.VALIDATED.value

        validated_file = self._workflow_dir / "validated.json"
        with open(validated_file, "w") as f:
            json.dump(self._state["validated_highlights"], f, indent=2)

    def _stage_complete(self):
        self._state["stage"] = WorkflowStage.COMPLETE.value
        self.save_state()

    def run_full(self) -> list[dict]:
        self.execute_stage(WorkflowStage.VALIDATED)
        return self._state["validated_highlights"]
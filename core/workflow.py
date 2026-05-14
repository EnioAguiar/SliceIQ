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

    @property
    def validated_highlights(self) -> list[dict]:
        return self._state.get("validated_highlights", [])

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

        if len(segments) > 500:
            step = len(segments) // 500
            sampled_segments = segments[::step]
            segments_text = "\n".join([
                f"[{s['start']:.1f}s - {s['end']:.1f}s]: {s['text']}"
                for s in sampled_segments
            ])
            logger.warning(f"Transcript sampled: {len(segments)} segments → {len(sampled_segments)} (1 of every {step})")

        duration_target = (self.profile.duration_min + self.profile.duration_max) / 2

        prompt = f"""Analise o transcript e identifique {num_candidates} momentos para video highlights.

DURAÇÃO ALVO: {self.profile.duration_min}s a {self.profile.duration_max}s por highlight
DICA: Para alcançar {duration_target:.0f}s, COMBINE múltiplos segmentos consecutivos do transcript.

COMO COMBINAR:
- Highlight NÃO precisa começar/endar em boundaries de segmento
- Você PODE usar: start=100.0, end=450.0 (mesmo que transcript mostre 100-105, 105-110, etc.)
- Combine segmentos que seguem naturalmente um do outro
- O texto entre start e end será concatenado automaticamente

REGRAS:
1. Duration = end - start DEVE estar entre {self.profile.duration_min}s e {self.profile.duration_max}s
2. PRIORIZAR durations perto de {duration_target:.0f}s (meio do range)
3. Highlights devem fazer sentido narrativo (conversa连贯, não cortado)
4. Timestamps com 1 casa decimal (ex: 125.5)

Output JSON:
{{"candidates": [
  {{"start": float, "end": float, "score": int, "reason": str}}
]}}

⚠️ REJEITADO se duration < {self.profile.duration_min}s ou > {self.profile.duration_max}s

Transcript (timestamps em segundos):
{segments_text}

Escolha {num_candidates} momentos que:
- Respeitam duration {self.profile.duration_min}-{self.profile.duration_max}s
- Têm continuidade narrativa (conteúdo连贯)
- Têm alto potencial viral/engagement"""

        logger.info(f"Calling LLM for {num_candidates} candidates...")
        response = self.analyzer._call_llm(prompt, num_candidates)
        logger.info(f"LLM response received, length: {len(response)} chars")
        candidates = self.analyzer._parse_response(response)
        logger.info(f"Parsed {len(candidates)} candidates")

        valid_candidates = []
        for c in candidates:
            duration = c.end - c.start
            if self.profile.duration_min <= duration <= self.profile.duration_max:
                valid_candidates.append(c)
            else:
                logger.warning(f"Candidate rejected: duration {duration:.1f}s outside range [{self.profile.duration_min:.0f}-{self.profile.duration_max:.0f}]")

        logger.info(f"Candidates: {len(valid_candidates)} valid / {len(candidates)} total")

        self._state["candidates"] = [
            {"start": c.start, "end": c.end, "score": c.score, "reason": c.reason}
            for c in valid_candidates
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

        target = (self.profile.duration_min + self.profile.duration_max) / 2
        duration_range = self.profile.duration_max - self.profile.duration_min

        prompt = f"""Avalie cada candidato quanto a 3 critérios com scores de 0-100:

1. HOOK_SCORE (40% do total): Quão forte é o início do highlight?
   - Pergunta retórica captura atenção? (ex: "Você sabia que...", "E se eu te dissesse que...")
   - Declaração impactante ou polêmica? (ex: "Ninguém esperava isso", "Isso vai mudar tudo")
   - Citação forte ou declaração definitiva? (ex: "Sempre disse que...", "Nunca ninguém fez isso")
   - SCORE ALTO: início com pergunta/declaração forte
   - SCORE BAIXO: início comum, sem destaque

2. VIRAL_SCORE (30% do total): Potencial para viralizar/engajar?
   - Número grande ou estatística impressionante? (ex: "97%", "milhões", "biliões")
   - Citação compartilhável? (frase que gente quer enviar)
   - Palavras fortes de impacto? (nunca, sempre, todo, ninguém, todos)
   - Polêmica ou controvérsia? (declarações fortes)
   - SCORE ALTO: contém elemento viral conhecido
   - SCORE BAIXO: conteúdo comum, sem elemento compartilhável

3. DURATION_SCORE (30% do total): Quão bem respeita a duração target?
   - Target: {target:.0f}s, Range: {duration_range:.0f}s ({self.profile.duration_min:.0f}s - {self.profile.duration_max:.0f}s)
   - Formula: score = 100 - (|duration - target| / range) * 100
   - Exemplo: se target={target:.0f}s e range={duration_range:.0f}s, uma duração de {target - duration_range/4:.0f}s teria score ~75
   - SCORE ALTO: duração próxima do target
   - SCORE BAIXO: duração longe do target (muito curto ou muito longo)

Duração real de cada candidato deve ser calculada como: end - start

Candidatos:
{candidates_list}

Raciocínio: Analisando cada candidato... penso sobre hook forte, elemento viral, e proximidade do target... calculo scores...

→ JSON Output (use duration_score baseado em formula, não apenas comply):
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

        target = (self.profile.duration_min + self.profile.duration_max) / 2
        duration_range = self.profile.duration_max - self.profile.duration_min

        data = json.loads(match.group())
        scored_list = []

        for item in data.get("scored", []):
            hook = item.get("hook_score", 50)
            viral = item.get("viral_score", 50)

            duration = item.get("end", 0) - item.get("start", 0)
            if duration_range > 0:
                duration_score = max(0, min(100, int(100 - (abs(duration - target) / duration_range) * 100)))
            else:
                duration_score = 50

            total = int(hook * 0.4 + viral * 0.3 + duration_score * 0.3)

            scored_list.append(ScoredHighlight(
                start=item["start"],
                end=item["end"],
                score=item.get("score", 50),
                reason=item.get("reason", ""),
                hook_score=hook,
                viral_score=viral,
                duration_score=duration_score,
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

        for item in selected:
            duration = item["end"] - item["start"]
            min_dur = self.profile.duration_min
            max_dur = self.profile.duration_max

            if duration < min_dur or duration > max_dur:
                continue

            if item.get("total_score", 0) < self.profile.score_minimum:
                continue

            validated.append(item)

        self._state["validated_highlights"] = validated
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
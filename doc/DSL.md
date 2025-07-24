Based on your game encyclopedia platform architecture and the Gambonanza analysis example, I'll design a comprehensive DSL structure that extends your existing data models to capture detailed game mechanics and analysis from video content.

## Enhanced DSL Structure

### Core Game Analysis Schema

```typescript
interface GameAnalysisEntry extends GameEntry {
  // Extended game identification
  analysis_id: string           // "GAMB-20240724-001"
  source_videos: VideoSource[]  // Original analysis sources
  analysis_timestamp: string    // When this analysis was generated
  confidence_score: number      // AI analysis confidence [0,1]
  
  // Core game classification
  primary_genre: string         // "Chess Roguelike"
  sub_genres: string[]         // ["Bullet Heaven", "Turn-based Strategy"]
  gameplay_tags: string[]      // ["Pawn Promotion", "Artifact System", "Boss Battles"]
  
  // Game systems architecture
  core_systems: GameSystem[]
  victory_conditions: VictoryCondition[]
  progression_mechanics: ProgressionMechanic[]
  
  // Faction/influence analysis
  design_influences: DesignInfluence[]
  innovation_factors: InnovationFactor[]
  
  // Localization support
  localized_content: Record<string, LocalizedGameContent>
}

interface GameSystem {
  system_id: string            // "relic_system"
  name: string                // "Relic/Artifact System"
  category: SystemCategory     // "progression" | "combat" | "economy" | "narrative"
  description: string         // Natural language description
  
  // System mechanics
  mechanics: SystemMechanic[]
  interactions: SystemInteraction[]
  balance_factors: BalanceFactor[]
  
  // Analysis metadata
  complexity_rating: number   // [1,5] complexity scale
  innovation_level: number    // [1,5] how innovative this system is
  player_agency: number       // [1,5] how much control player has
}

interface SystemMechanic {
  mechanic_id: string         // "thunder_gambit_skip_turn"
  name: string               // "Thunder's Gambit"
  type: MechanicType         // "trigger" | "passive" | "active" | "condition"
  trigger_condition: string  // "Pawn captures enemy piece"
  effect_description: string // "Skip enemy turn, continue player turn"
  
  // Mechanical properties
  rarity: RarityLevel        // "common" | "rare" | "epic" | "legendary"
  power_level: number        // [1,10] mechanical impact
  synergy_potential: number  // [1,10] combo potential
  
  // Balancing
  cost: ResourceCost[]       // What it costs to obtain/use
  limitations: string[]      // Restrictions or downsides
  counterplay: string[]      // How opponents can respond
}

interface VictoryCondition {
  condition_id: string       // "eliminate_all_enemies"
  description: string        // "Capture all enemy pieces"
  type: ConditionType        // "elimination" | "objective" | "survival" | "score"
  requirements: Requirement[]
  alternative_paths: string[] // Other ways to achieve this condition
}

interface ProgressionMechanic {
  progression_id: string     // "piece_promotion"
  name: string              // "Pawn Promotion System"
  category: ProgressionType // "character" | "equipment" | "skill" | "unlock"
  
  // Progression structure
  stages: ProgressionStage[]
  unlock_conditions: UnlockCondition[]
  rewards: ProgressionReward[]
  
  // Meta-progression
  permanent_upgrades: boolean
  reset_frequency: ResetFrequency // "never" | "run" | "session" | "periodic"
}

interface DesignInfluence {
  influence_id: string       // "vampire_survivors_influence"
  source_game: string        // "Vampire Survivors"
  influence_type: InfluenceType // "mechanical" | "aesthetic" | "narrative" | "ui_ux"
  
  // Influence analysis
  inherited_elements: string[]   // ["bullet_heaven_genre", "auto_combat"]
  adaptation_method: string      // How it was adapted/modified
  innovation_added: string       // What new elements were introduced
  
  // Quantitative measures
  similarity_score: number       // [0,1] how similar the implementation is
  influence_weight: number       // [0,1] how much this influenced the game
}
```

### Video Analysis Integration

```typescript
interface EnhancedVideoChunk extends VideoChunk {
  // Enhanced content analysis
  game_mechanics_mentioned: GameMechanicReference[]
  strategy_insights: StrategyInsight[]
  player_reactions: PlayerReaction[]
  
  // Semantic analysis
  key_moments: KeyMoment[]
  difficulty_assessment: DifficultyMoment[]
  balance_commentary: BalanceOpinion[]
  
  // Cross-reference data
  referenced_games: GameReference[]
  comparison_points: ComparisonPoint[]
}

interface GameMechanicReference {
  mechanic_name: string          // "Thunder's Gambit"
  mention_context: MentionContext // "explanation" | "demonstration" | "critique"
  timestamp_range: TimeRange
  
  // Analysis data
  player_understanding_level: number // [1,5] how well player understands it
  effectiveness_rating: number       // [1,5] how effective player finds it
  emotional_response: EmotionalTag[] // ["excitement", "frustration", "satisfaction"]
}

interface StrategyInsight {
  insight_id: string
  category: InsightCategory      // "optimization" | "discovery" | "counter_strategy"
  description: string           // Natural language insight
  
  // Strategic value
  skill_level_required: SkillLevel // "beginner" | "intermediate" | "advanced" | "expert"
  applicability: ApplicabilityScope // "universal" | "situational" | "niche"
  meta_relevance: number          // [0,1] how relevant to current meta
}
```

### Analysis Processing Pipeline

```typescript
interface AnalysisProcessingResult {
  processing_id: string
  source_content: SourceContent[]
  
  // LLM analysis stages
  extraction_results: ExtractionStage
  classification_results: ClassificationStage
  synthesis_results: SynthesisStage
  
  // Quality metrics
  analysis_quality: QualityMetrics
  validation_status: ValidationStatus
  human_review_flags: ReviewFlag[]
}

interface ExtractionStage {
  stage_name: "extraction"
  extracted_entities: ExtractedEntity[]
  confidence_scores: Record<string, number>
  
  // Raw extractions
  mentioned_games: string[]
  identified_mechanics: string[]
  found_strategies: string[]
  detected_emotions: EmotionalMarker[]
}

interface ClassificationStage {
  stage_name: "classification"
  genre_classification: GenreClassification
  system_categorization: SystemCategorization
  influence_mapping: InfluenceMapping
  
  // Classification confidence
  classification_certainty: number
  alternative_classifications: AlternativeClassification[]
}

interface SynthesisStage {
  stage_name: "synthesis"
  final_game_profile: GameAnalysisEntry
  relationship_mapping: RelationshipMap
  trend_analysis: TrendAnalysis
  
  // Synthesis quality
  coherence_score: number        // [0,1] how coherent the final analysis is
  completeness_score: number     // [0,1] how complete the analysis is
  novelty_score: number         // [0,1] how novel the insights are
}
```

### Implementation Integration Points

For your existing architecture, this DSL integrates as follows:

**crawler-svc** would populate the raw VideoChunk and basic GameEntry data, while **context-svc** would use LLM processing to generate the enhanced GameAnalysisEntry structures. The **wiki-web** frontend would consume these rich data structures to create the interactive visualizations and relationship graphs you've outlined.

The schema supports your faction influence analysis goals by providing structured influence tracking, while maintaining flexibility for various game types and analysis depths. The multi-stage processing pipeline ensures quality control and allows for iterative refinement of the analysis results.

This structure scales from simple game identification to complex mechanical analysis, supporting both your MVP goals and long-term vision for comprehensive game design pattern recognition.
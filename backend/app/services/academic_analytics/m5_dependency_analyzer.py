class M5DependencyAnalyzer:
    """
    M5.5 — Dependency / Prerequisite Graph Analyzer

    Converts prerequisite information from M4 into a
    usable dependency graph.

    Example:

        Proactive vs Reactive Routing
                    ↓
              Hybrid Routing

    M5.5 does NOT call the LLM.

    It:
        1. Builds the prerequisite graph
        2. Separates valid and unresolved prerequisites
        3. Detects circular dependencies
        4. Removes cyclic edges from the usable graph
        5. Finds dependent topics
        6. Calculates dependency depth
        7. Preserves all useful analytics

    Important:
        M4 can occasionally produce:
            - a prerequisite ID that is not present
            - circular prerequisite relationships

        Neither should crash the entire M5 pipeline.
    """

    def __init__(
        self,
        topic_analytics: list[dict],
    ):
        """
        Receive M5.4 topic analytics.
        """

        self.topic_analytics = topic_analytics

        # Fast lookup:
        #
        # topic_id -> topic record

        self.topic_map = {
            topic["topic_id"]: topic
            for topic in topic_analytics
        }

    # ======================================================
    # MAIN ANALYSIS
    # ======================================================

    def analyze(self) -> list[dict]:
        """
        Build the complete M5.5 dependency analysis.
        """

        # --------------------------------------------------
        # STEP 1 — BUILD RAW GRAPH
        # --------------------------------------------------

        raw_graph = self._build_graph()

        # --------------------------------------------------
        # STEP 2 — REMOVE INVALID / UNRESOLVED IDS
        # --------------------------------------------------

        (
            valid_graph,
            unresolved,
        ) = self._validate_prerequisites(
            raw_graph
        )

        # --------------------------------------------------
        # STEP 3 — FIND CYCLES
        # --------------------------------------------------

        cycles = self._find_all_cycles(
            valid_graph
        )

        # --------------------------------------------------
        # STEP 4 — REMOVE CYCLIC EDGES
        # --------------------------------------------------
        #
        # We don't arbitrarily change the original M4 data.
        #
        # Instead:
        #
        #   valid_graph
        #       ↓
        #   usable_graph
        #
        # Cyclic relationships are recorded separately.

        usable_graph = self._remove_cyclic_edges(
            valid_graph,
            cycles
        )

        # --------------------------------------------------
        # STEP 5 — REVERSE GRAPH
        # --------------------------------------------------

        dependents = (
            self._build_reverse_graph(
                usable_graph
            )
        )

        # --------------------------------------------------
        # STEP 6 — DEPENDENCY DEPTH
        # --------------------------------------------------

        depth_cache = {}

        for topic_id in self.topic_map:

            self._calculate_depth(
                topic_id=topic_id,
                graph=usable_graph,
                cache=depth_cache,
            )

        # --------------------------------------------------
        # STEP 7 — BUILD FINAL RESULTS
        # --------------------------------------------------

        results = []

        for topic in self.topic_analytics:

            topic_id = topic[
                "topic_id"
            ]

            prerequisite_ids = (
                usable_graph.get(
                    topic_id,
                    []
                )
            )

            unresolved_ids = (
                unresolved.get(
                    topic_id,
                    []
                )
            )

            dependent_ids = (
                dependents.get(
                    topic_id,
                    []
                )
            )

            # Find cycles involving this topic.

            topic_cycles = [
                cycle
                for cycle in cycles
                if topic_id in cycle
            ]

            result = {
                # ------------------------------------------
                # TOPIC INFORMATION
                # ------------------------------------------

                "topic_id": topic_id,

                "topic": topic[
                    "topic"
                ],

                "subtopic": topic[
                    "subtopic"
                ],

                "unit": topic[
                    "unit"
                ],

                # ------------------------------------------
                # IMPORTANCE
                # ------------------------------------------

                "importance_score": topic[
                    "importance_score"
                ],

                "priority": topic[
                    "priority"
                ],

                # ------------------------------------------
                # USABLE PREREQUISITES
                # ------------------------------------------

                "prerequisites": (
                    prerequisite_ids
                ),

                "prerequisite_count": (
                    len(prerequisite_ids)
                ),

                # ------------------------------------------
                # UNRESOLVED PREREQUISITES
                # ------------------------------------------

                "unresolved_prerequisites": (
                    unresolved_ids
                ),

                "unresolved_prerequisite_count": (
                    len(unresolved_ids)
                ),

                # ------------------------------------------
                # CIRCULAR DEPENDENCIES
                # ------------------------------------------

                "dependency_cycles": (
                    topic_cycles
                ),

                "cycle_count": (
                    len(topic_cycles)
                ),

                # ------------------------------------------
                # DEPENDENT TOPICS
                # ------------------------------------------

                "dependent_topics": (
                    dependent_ids
                ),

                "dependent_count": (
                    len(dependent_ids)
                ),

                # ------------------------------------------
                # DEPENDENCY DEPTH
                # ------------------------------------------

                "dependency_depth": (
                    depth_cache[topic_id]
                ),

                # ------------------------------------------
                # PREREQUISITE FLAG
                # ------------------------------------------

                "is_prerequisite": (
                    len(dependent_ids) > 0
                ),

                # ------------------------------------------
                # EXAM STATISTICS
                # ------------------------------------------

                "question_count": topic[
                    "question_count"
                ],

                "paper_count": topic[
                    "paper_count"
                ],

                "total_marks": topic[
                    "total_marks"
                ],

                "average_marks": topic[
                    "average_marks"
                ],

                # ------------------------------------------
                # ACTUAL QUESTIONS
                # ------------------------------------------

                "questions": topic[
                    "questions"
                ],

                "papers": topic[
                    "papers"
                ],
            }

            results.append(
                result
            )

        # --------------------------------------------------
        # STEP 8 — SORT
        # --------------------------------------------------

        # Topics with smaller dependency depth appear
        # earlier because they are easier starting points.

        results.sort(
            key=lambda item: (
                item["dependency_depth"],
                -item["importance_score"],
                item["topic_id"],
            )
        )

        return results

    # ======================================================
    # BUILD RAW GRAPH
    # ======================================================

    def _build_graph(
        self,
    ) -> dict[str, list[str]]:
        """
        Build:

            topic_id -> prerequisite IDs
        """

        graph = {}

        for topic in self.topic_analytics:

            topic_id = topic[
                "topic_id"
            ]

            prerequisites = topic.get(
                "prerequisites",
                []
            )

            # Remove duplicate prerequisite IDs.

            unique_prerequisites = list(
                dict.fromkeys(
                    prerequisites
                )
            )

            graph[
                topic_id
            ] = unique_prerequisites

        return graph

    # ======================================================
    # VALIDATE PREREQUISITES
    # ======================================================

    def _validate_prerequisites(
        self,
        graph: dict[str, list[str]],
    ) -> tuple[
        dict[str, list[str]],
        dict[str, list[str]],
    ]:
        """
        Separate prerequisite IDs into:

            valid
            unresolved

        Example:

            Topic A:
                [B, X]

            B exists.
            X doesn't exist.

        Result:

            valid_graph[A] = [B]

            unresolved[A] = [X]
        """

        valid_ids = set(
            self.topic_map.keys()
        )

        valid_graph = {}

        unresolved = {}

        for topic_id, prerequisites in (
            graph.items()
        ):

            valid_prerequisites = []

            unresolved_prerequisites = []

            for prerequisite_id in (
                prerequisites
            ):

                # ------------------------------------------
                # SELF DEPENDENCY
                # ------------------------------------------

                if (
                    prerequisite_id
                    == topic_id
                ):

                    # Treat self-reference as unresolved
                    # instead of crashing.

                    unresolved_prerequisites.append(
                        prerequisite_id
                    )

                    continue

                # ------------------------------------------
                # VALID
                # ------------------------------------------

                if (
                    prerequisite_id
                    in valid_ids
                ):

                    valid_prerequisites.append(
                        prerequisite_id
                    )

                # ------------------------------------------
                # UNKNOWN
                # ------------------------------------------

                else:

                    unresolved_prerequisites.append(
                        prerequisite_id
                    )

            valid_graph[
                topic_id
            ] = valid_prerequisites

            if unresolved_prerequisites:

                unresolved[
                    topic_id
                ] = unresolved_prerequisites

        return (
            valid_graph,
            unresolved,
        )

    # ======================================================
    # FIND ALL CYCLES
    # ======================================================

    def _find_all_cycles(
        self,
        graph: dict[str, list[str]],
    ) -> list[list[str]]:
        """
        Find circular prerequisite relationships.

        Example:

            A -> B
            B -> A

        gives:

            [A, B, A]

        We collect cycles rather than throwing an error.
        """

        cycles = []

        visited = set()

        def dfs(
            node: str,
            path: list[str],
            path_set: set[str],
        ):

            path.append(node)

            path_set.add(node)

            for neighbor in graph.get(
                node,
                []
            ):

                # ------------------------------------------
                # CYCLE FOUND
                # ------------------------------------------

                if neighbor in path_set:

                    start_index = (
                        path.index(
                            neighbor
                        )
                    )

                    cycle = (
                        path[
                            start_index:
                        ]
                        + [neighbor]
                    )

                    # Avoid duplicate cycles.

                    cycle_key = tuple(
                        cycle
                    )

                    existing_keys = {
                        tuple(existing)
                        for existing in cycles
                    }

                    if (
                        cycle_key
                        not in existing_keys
                    ):

                        cycles.append(
                            cycle
                        )

                    continue

                # ------------------------------------------
                # CONTINUE DFS
                # ------------------------------------------

                if neighbor not in visited:

                    dfs(
                        neighbor,
                        path,
                        path_set,
                    )

            path.pop()

            path_set.remove(node)

            visited.add(node)

        for node in graph:

            if node not in visited:

                dfs(
                    node,
                    [],
                    set(),
                )

        return cycles

    # ======================================================
    # REMOVE CYCLIC EDGES
    # ======================================================

    def _remove_cyclic_edges(
        self,
        graph: dict[str, list[str]],
        cycles: list[list[str]],
    ) -> dict[str, list[str]]:
        """
        Remove edges participating in circular dependencies.

        Example:

            A -> B
            B -> A

        Both edges are removed from the usable graph.

        The original cycle remains available through
        dependency_cycles in the final output.
        """

        usable_graph = {
            topic_id: list(
                prerequisites
            )
            for topic_id, prerequisites
            in graph.items()
        }

        for cycle in cycles:

            if len(cycle) < 2:
                continue

            # A -> B -> A

            for index in range(
                len(cycle) - 1
            ):

                source = cycle[
                    index
                ]

                target = cycle[
                    index + 1
                ]

                if (
                    source
                    in usable_graph
                ):

                    if (
                        target
                        in usable_graph[source]
                    ):

                        usable_graph[
                            source
                        ].remove(
                            target
                        )

        return usable_graph

    # ======================================================
    # REVERSE GRAPH
    # ======================================================

    def _build_reverse_graph(
        self,
        graph: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        """
        Convert:

            B -> [A]

        into:

            A -> [B]

        Meaning:

            B depends on A.
        """

        reverse_graph = {
            topic_id: []
            for topic_id in graph
        }

        for topic_id, prerequisites in (
            graph.items()
        ):

            for prerequisite_id in (
                prerequisites
            ):

                if (
                    prerequisite_id
                    not in reverse_graph
                ):
                    continue

                reverse_graph[
                    prerequisite_id
                ].append(
                    topic_id
                )

        # Deterministic output.

        for topic_id in reverse_graph:

            reverse_graph[
                topic_id
            ].sort()

        return reverse_graph

    # ======================================================
    # DEPENDENCY DEPTH
    # ======================================================

    def _calculate_depth(
        self,
        topic_id: str,
        graph: dict[str, list[str]],
        cache: dict[str, int],
    ) -> int:
        """
        Calculate dependency depth.

        Example:

            A
            ↓
            B
            ↓
            C

            A = 0
            B = 1
            C = 2
        """

        # Already calculated.

        if topic_id in cache:

            return cache[
                topic_id
            ]

        prerequisites = graph.get(
            topic_id,
            []
        )

        # No prerequisites.

        if not prerequisites:

            cache[
                topic_id
            ] = 0

            return 0

        max_depth = 0

        for prerequisite_id in (
            prerequisites
        ):

            prerequisite_depth = (
                self._calculate_depth(
                    topic_id=prerequisite_id,
                    graph=graph,
                    cache=cache,
                )
            )

            max_depth = max(
                max_depth,
                prerequisite_depth,
            )

        depth = (
            max_depth + 1
        )

        cache[
            topic_id
        ] = depth

        return depth
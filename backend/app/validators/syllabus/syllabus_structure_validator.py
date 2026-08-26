class SyllabusStructureValidator:

    @staticmethod
    def validate(
        syllabus_data: list,
    ) -> dict:

        errors = []
        warnings = []

        total_courses = 0
        total_units = 0
        total_topics = 0
        total_subtopics = 0

        # ======================================================
        # 1. CHECK TOP-LEVEL DATA
        # ======================================================

        if not isinstance(syllabus_data, list):

            errors.append(
                "Syllabus data must be a list of courses."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "stats": {},
            }

        if not syllabus_data:

            errors.append(
                "No courses found in syllabus."
            )

            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings,
                "stats": {},
            }

        # ======================================================
        # 2. CHECK COURSES
        # ======================================================

        course_codes = set()

        for course_index, course in enumerate(
            syllabus_data,
            start=1,
        ):

            total_courses += 1

            # --------------------------------------------------
            # Course must be dictionary
            # --------------------------------------------------

            if not isinstance(course, dict):

                errors.append(
                    f"Course {course_index} "
                    f"is not a valid object."
                )

                continue

            course_code = course.get(
                "course_code"
            )

            course_name = course.get(
                "course_name"
            )

            # --------------------------------------------------
            # Course code
            # --------------------------------------------------

            if not course_code:

                errors.append(
                    f"Course {course_index} "
                    f"has missing course_code."
                )

                course_label = (
                    f"Course {course_index}"
                )

            else:

                course_label = str(
                    course_code
                )

                # Duplicate course
                if course_code in course_codes:

                    errors.append(
                        f"Duplicate course: "
                        f"{course_code}"
                    )

                course_codes.add(
                    course_code
                )

            # --------------------------------------------------
            # Course name
            # --------------------------------------------------

            if not course_name:

                errors.append(
                    f"{course_label} "
                    f"has missing course_name."
                )

            # --------------------------------------------------
            # Units
            # --------------------------------------------------

            units = course.get(
                "units"
            )

            if not isinstance(
                units,
                list,
            ):

                errors.append(
                    f"{course_label} "
                    f"has invalid units structure."
                )

                continue

            if not units:

                errors.append(
                    f"{course_label} "
                    f"has no units."
                )

                continue

            # ==================================================
            # 3. CHECK UNITS
            # ==================================================

            unit_numbers = set()

            for unit_index, unit in enumerate(
                units,
                start=1,
            ):

                total_units += 1

                if not isinstance(
                    unit,
                    dict,
                ):

                    errors.append(
                        f"{course_label}: "
                        f"Unit {unit_index} "
                        f"is not a valid object."
                    )

                    continue

                unit_number = unit.get(
                    "unit_number"
                )

                # ------------------------------------------------
                # Unit number
                # ------------------------------------------------

                if unit_number is None:

                    errors.append(
                        f"{course_label}: "
                        f"Unit {unit_index} "
                        f"has missing unit_number."
                    )

                    unit_label = (
                        f"Unit {unit_index}"
                    )

                else:

                    unit_label = (
                        f"Unit {unit_number}"
                    )

                    if unit_number in unit_numbers:

                        errors.append(
                            f"{course_label}: "
                            f"Duplicate "
                            f"{unit_label}."
                        )

                    unit_numbers.add(
                        unit_number
                    )

                # ------------------------------------------------
                # Topics
                # ------------------------------------------------

                topics = unit.get(
                    "topics"
                )

                if not isinstance(
                    topics,
                    list,
                ):

                    errors.append(
                        f"{course_label} "
                        f"{unit_label}: "
                        f"topics must be a list."
                    )

                    continue

                if not topics:

                    errors.append(
                        f"{course_label} "
                        f"{unit_label}: "
                        f"no topics found."
                    )

                    continue

                # =================================================
                # 4. CHECK TOPICS
                # =================================================

                topic_names = set()

                for topic_index, topic in enumerate(
                    topics,
                    start=1,
                ):

                    total_topics += 1

                    if not isinstance(
                        topic,
                        dict,
                    ):

                        errors.append(
                            f"{course_label} "
                            f"{unit_label}: "
                            f"Topic {topic_index} "
                            f"is not a valid object."
                        )

                        continue

                    topic_name = topic.get(
                        "topic"
                    )

                    # ------------------------------------------------
                    # Topic name
                    # ------------------------------------------------

                    if not isinstance(
                        topic_name,
                        str,
                    ) or not topic_name.strip():

                        errors.append(
                            f"{course_label} "
                            f"{unit_label}: "
                            f"Topic {topic_index} "
                            f"has empty topic name."
                        )

                    else:

                        normalized_topic = (
                            topic_name
                            .strip()
                            .lower()
                        )

                        if (
                            normalized_topic
                            in topic_names
                        ):

                            errors.append(
                                f"{course_label} "
                                f"{unit_label}: "
                                f"Duplicate topic: "
                                f"{topic_name}"
                            )

                        topic_names.add(
                            normalized_topic
                        )

                    # ------------------------------------------------
                    # Subtopics
                    # ------------------------------------------------

                    subtopics = topic.get(
                        "subtopics"
                    )

                    if subtopics is None:

                        warnings.append(
                            f"{course_label} "
                            f"{unit_label}: "
                            f"Topic '{topic_name}' "
                            f"has no subtopics field."
                        )

                        continue

                    if not isinstance(
                        subtopics,
                        list,
                    ):

                        errors.append(
                            f"{course_label} "
                            f"{unit_label}: "
                            f"Topic '{topic_name}' "
                            f"has invalid subtopics."
                        )

                        continue

                    # Empty subtopics = warning
                    if not subtopics:

                        warnings.append(
                            f"{course_label} "
                            f"{unit_label}: "
                            f"Topic '{topic_name}' "
                            f"has no subtopics."
                        )

                    # ------------------------------------------------
                    # Validate every subtopic
                    # ------------------------------------------------

                    subtopic_names = set()

                    for subtopic_index, subtopic in enumerate(
                        subtopics,
                        start=1,
                    ):

                        if not isinstance(
                            subtopic,
                            str,
                        ) or not subtopic.strip():

                            errors.append(
                                f"{course_label} "
                                f"{unit_label}: "
                                f"Topic '{topic_name}' "
                                f"has empty/invalid "
                                f"subtopic {subtopic_index}."
                            )

                            continue

                        total_subtopics += 1

                        normalized_subtopic = (
                            subtopic
                            .strip()
                            .lower()
                        )

                        if (
                            normalized_subtopic
                            in subtopic_names
                        ):

                            errors.append(
                                f"{course_label} "
                                f"{unit_label}: "
                                f"Topic '{topic_name}' "
                                f"has duplicate "
                                f"subtopic: "
                                f"{subtopic}"
                            )

                        subtopic_names.add(
                            normalized_subtopic
                        )

        # ======================================================
        # 5. FINAL RESULT
        # ======================================================

        return {

            "valid": len(errors) == 0,

            "errors": errors,

            "warnings": warnings,

            "stats": {

                "courses": total_courses,

                "units": total_units,

                "topics": total_topics,

                "subtopics": total_subtopics,
            },
        }
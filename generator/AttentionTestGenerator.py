import random
import math

class AttentionTestGenerator:
    # Connectors used when grouping multiple statements into one sentence.
    # Applied between stripped-period clauses; actor names are kept as-is (no lowercasing).
    STATEMENT_CONNECTORS = [
        ", and ",
        "; ",
        ", also ",
        ", while ",
        ", meanwhile ",
    ]

    def __init__(self, items, gain_loss, actors, abstract_generic, numbers, prompt_templates):
        self.items = items
        self.gain_verbs = gain_loss["gain_verbs"]
        self.loss_verbs = gain_loss["loss_verbs"]
        self.actors_ua = actors["ukrainian"]
        self.actors_non_ua = actors["non_ukrainian"]
        self.abstract_generic = []
        for cat in abstract_generic.values():
            self.abstract_generic.extend(cat)
        self.numbers = numbers
        self.prompts = prompt_templates

    def _get_number_str(self, n, ratio):
        if random.random() < ratio:
            return self.numbers.get(str(n), str(n))
        return str(n)

    def _get_n(self, multi_digit_ratio):
        if random.random() < multi_digit_ratio:
            return random.randint(10, 99)
        return random.randint(1, 9)

    def _select_actor(self, group):
        return random.choice(group)

    def _get_target_items(self, target_max_length, num_targets, target_min_length=1):
        valid = [
            i for i in self.items
            if i.get("can_be_target", False)
            and i.get("length", 1) <= target_max_length
            and i.get("length", 1) >= target_min_length
        ]
        if not valid:
            # Fallback: relax min-length constraint rather than crashing
            valid = [i for i in self.items if i.get("can_be_target", False) and i.get("length", 1) <= target_max_length]
        if not valid:
            valid = [i for i in self.items if i.get("can_be_target", False)]
        return random.sample(valid, min(num_targets, len(valid)))

    def _pluralize(self, phrase):
        """Pluralize the last word of a distractor phrase.

        Handles the common English patterns present in items.json distractors:
          - already-plural forms ending in 'es'  → unchanged  (eyeglasses)
          - words ending in 'ss'                 → + 'es'     (glass → glasses)
          - words ending in x / z / ch / sh      → + 'es'     (box → boxes)
          - words ending in consonant + y         → y → 'ies' (party → parties)
          - everything else                       → + 's'      (chip → chips)
        """
        words = phrase.split()
        w = words[-1]
        if w.endswith('es'):
            pass                                        # already plural
        elif w.endswith('ss'):
            w += 'es'                                   # glass → glasses
        elif w.endswith(('x', 'z', 'ch', 'sh')):
            w += 'es'                                   # box → boxes, pouch → pouches
        elif w.endswith('y') and len(w) > 1 and w[-2] not in 'aeiou':
            w = w[:-1] + 'ies'                         # party → parties
        elif w.endswith('s'):
            pass                                        # already plural (scissors, etc.)
        else:
            w += 's'
        return ' '.join(words[:-1] + [w])

    def _get_distractor_items(self, targets):
        target_ids = {t["identifier"] for t in targets}
        return [i for i in self.items if i["identifier"] not in target_ids]

    def _group_statements(self, statements, grouping_max):
        """Group consecutive statements into combined sentences using random connectors.

        E.g. with grouping_max=2:
          "Petro got 3 apples." + "Anna got 2 oranges."
          → "Petro got 3 apples, and Anna got 2 oranges."
        """
        if grouping_max <= 1:
            return statements

        result = []
        i = 0
        while i < len(statements):
            group_size = random.randint(1, min(grouping_max, len(statements) - i))
            group = statements[i:i + group_size]
            if len(group) == 1:
                result.append(group[0])
            else:
                parts = [s.rstrip('.') for s in group]
                combined = parts[0]
                for part in parts[1:]:
                    connector = random.choice(self.STATEMENT_CONNECTORS)
                    combined += connector + part
                combined += "."
                result.append(combined)
            i += group_size
        return result

    def generate(self, config, seed=None):
        if seed is not None:
            random.seed(seed)

        # 1. Parse Parameters
        num_statements = int(config['num_statements'])
        allow_negative = config['allow_negative'] == 'True'
        distractor_ratio = float(config['distractor_ratio'])
        abstract_ratio = float(config['abstract_ratio'])
        word_number_ratio = float(config['word_number_ratio'])
        multi_digit_ratio = float(config['multi_digit_ratio'])
        target_max_length = int(config['target_max_length'])
        num_targets = int(config['num_targets'])
        # Default to 1 (no grouping) if column is absent from older configs
        statements_grouping_max = int(config.get('statements_grouping_max', 1))
        target_min_length = int(config.get('target_min_length', 1))

        # 2. Setup Actors & Group Tracking
        group_size = random.randint(3, 8)
        half = max(1, group_size // 2)
        actor_pool = random.sample(self.actors_ua, half) + random.sample(self.actors_non_ua, group_size - half)
        random.shuffle(actor_pool)

        # Initialize dictionary to prevent negative balances
        # {actor: {target_id: amount}}
        actor_inventory = {actor: {} for actor in actor_pool}

        # 3. Select Targets
        targets = self._get_target_items(target_max_length, num_targets, target_min_length)
        target_ids = [t["identifier"] for t in targets]

        for t in target_ids:
            for a in actor_inventory:
                actor_inventory[a][t] = 0

        distractor_pool = self._get_distractor_items(targets)

        # Determine number of distractors vs targets
        num_distractors = int(math.floor(num_statements * distractor_ratio))
        num_relevant = num_statements - num_distractors

        statements = []

        # 4. Generate Relevant Statements
        for _ in range(num_relevant):
            t_item = random.choice(targets)
            t_id = t_item["identifier"]
            actor = self._select_actor(actor_pool)

            # Decide gain or loss
            can_lose = allow_negative and actor_inventory[actor][t_id] > 0
            is_gain = True
            if can_lose:
                is_gain = random.random() < 0.6 # slightly bias towards gains

            if is_gain:
                n = self._get_n(multi_digit_ratio)
                verb = random.choice(self.gain_verbs + t_item.get("additional_gain", []))
                # Filtering out not applicable
                while verb in t_item.get("not_applicable_gain", []):
                    verb = random.choice(self.gain_verbs + t_item.get("additional_gain", []))
                actor_inventory[actor][t_id] += n
            else:
                max_loss = actor_inventory[actor][t_id]
                n = random.randint(1, max_loss) # Strict rule: only lose what you have
                verb = random.choice(self.loss_verbs + t_item.get("additional_loss", []))
                while verb in t_item.get("not_applicable_loss", []):
                    verb = random.choice(self.loss_verbs + t_item.get("additional_loss", []))
                actor_inventory[actor][t_id] -= n

            n_str = self._get_number_str(n, word_number_ratio)
            noun = t_item["singular"] if n == 1 else t_item["plural"]
            statements.append(f"{actor} {verb} {n_str} {noun}.")

        # 5. Generate Distractors
        for _ in range(num_distractors):
            actor = self._select_actor(actor_pool)

            # Are we doing an abstract trap or a physical distractor?
            is_abstract = random.random() < abstract_ratio

            if is_abstract:
                # 50/50 generic abstract vs item-specific abstract trap
                if random.random() < 0.5 and any(t.get("abstract_stories") for t in targets):
                    # Item specific trap
                    valid_targets = [t for t in targets if t.get("abstract_stories")]
                    trap_target = random.choice(valid_targets)
                    trap_sentence = random.choice(trap_target["abstract_stories"])
                    n = self._get_n(multi_digit_ratio)
                    n_str = self._get_number_str(n, word_number_ratio)
                    res = trap_sentence.replace("{actor}", actor).replace("{n}", n_str)
                    statements.append(res)
                else:
                    # Generic trap
                    base_concept = random.choice(distractor_pool)
                    trap_sentence = random.choice(self.abstract_generic)
                    n = self._get_n(multi_digit_ratio)
                    n_str = self._get_number_str(n, word_number_ratio)
                    noun = base_concept["singular"] if n == 1 else base_concept["plural"]
                    res = trap_sentence.replace("{actor}", actor).replace("{n}", n_str).replace("{target}", noun)
                    statements.append(res)
            else:
                # Physical Distractor interactions
                # Substring Weaponization: If target length > 1, use its short form
                use_substring = False
                for t in targets:
                    if t.get("length", 1) > 1 and random.random() < 0.3:
                        use_substring = True
                        phys_noun = t["base_noun"]
                        # We force plural > 1 override for string distractors
                        n = random.randint(2, 99)
                        phys_noun_plural = phys_noun + "s"
                        break

                if not use_substring:
                    # Pick random distractor item or string
                    d = random.choice(distractor_pool)
                    if random.random() < 0.5 and d.get("distractors"):
                        # Pick a raw distractor string; always n>1 (Rule 1), so pluralize
                        raw_str = random.choice(d["distractors"])
                        n = random.randint(2, 99) # Rule 1: Plurality override n > 1
                        phys_noun_plural = self._pluralize(raw_str)
                    else:
                        n = self._get_n(multi_digit_ratio)
                        phys_noun_plural = d["singular"] if n == 1 else d["plural"]

                n_str = self._get_number_str(n, word_number_ratio)
                v = random.choice(self.gain_verbs)
                statements.append(f"{actor} {v} {n_str} {phys_noun_plural}.")

        # 6. Interleave Chronologically
        random.shuffle(statements)

        # 7. Math Computation (grouping happens after all statements are finalised)
        group_totals = {t: 0 for t in target_ids}
        for a in actor_inventory:
            for t in target_ids:
                group_totals[t] += actor_inventory[a][t]

        # Zero-Bound Safety Constraint: no 0 expected answers
        for t in target_ids:
            if group_totals[t] == 0:
                actor = self._select_actor(actor_pool)
                verb = random.choice(self.gain_verbs)
                t_item = next(item for item in targets if item["identifier"] == t)
                while verb in t_item.get("not_applicable_gain", []):
                    verb = random.choice(self.gain_verbs + t_item.get("additional_gain", []))
                n = self._get_n(multi_digit_ratio)
                n_str = self._get_number_str(n, word_number_ratio)
                noun = t_item["singular"] if n == 1 else t_item["plural"]
                statements.append(f"{actor} {verb} {n_str} {noun}.")
                actor_inventory[actor][t] += n
                group_totals[t] += n

        # Final shuffle (covers both normal path and zero-safety append), then group once
        random.shuffle(statements)
        statements = self._group_statements(statements, statements_grouping_max)
        story = " ".join(statements)

        # 9. Prompt Assembly — use plural forms in the question so we don't mislead the model
        if num_targets == 1:
            final_answer = group_totals[target_ids[0]]
            prompt_type = "simple" if distractor_ratio == 0 else "detailed"
            pt = self.prompts[prompt_type]
            t_item = next(item for item in targets if item["identifier"] == target_ids[0])
            q = pt["question_template"].replace("{story}", story).replace("{target}", t_item["plural"])
        else:
            final_answer = 1
            for t in target_ids:
                final_answer *= group_totals[t]
            pt = self.prompts["multi_target"]
            # Use plural forms for all targets in multi-target question
            tgt_str = ", ".join(
                next(item for item in targets if item["identifier"] == t)["plural"]
                for t in target_ids
            )
            q = pt["question_template"].replace("{story}", story).replace("{targets}", tgt_str)

        full_prompt = f"{pt['system_prompt']}\n\n{q}"

        return {
            "prompt": full_prompt,
            "story": story,
            "target_words": target_ids,
            "ground_truth_answer": final_answer,
            "actor_end_balances": actor_inventory,
            "configuration": config
        }

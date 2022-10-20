import pydle
import markovify
import re
from .secrets import *
from .utils import normalize_nick, normalize_lover
from collections import defaultdict
from hashlib import md5
from random import choice


class CustomNewlineText(markovify.NewlineText):
    def __init__(self, input_text, *args, **kwargs):
        super(markovify.NewlineText, self).__init__(input_text, *args, **kwargs)
        self.size = len(input_text)


class Marchov(pydle.Client):
    def __init__(self, *args, **kwargs):
        self.models = {}
        self.tintin = []
        super(pydle.Client, self).__init__(*args, **kwargs)

    def recreate_models(self):
        messages = defaultdict(list)
        with open(MARKOV_INPUT, "r") as f:
            corpus = f.read().splitlines()
        for idx, line in enumerate(corpus):
            fields = line.split()
            if len(fields) >= 3:
                nick = fields[2]
            else:
                continue
            if nick in ("*", "--", "<--", "-->"):
                continue
            nick = normalize_nick(nick)
            message = " ".join(fields[3:])
            messages[nick].append(message)
        for nick in sorted(messages.keys()):
            print(f"Commence {nick}")
            try:
                model = CustomNewlineText("\n".join(messages[nick]), state_size=3)
                self.models[nick] = model
            except KeyError:
                pass
        print("Modèles recréés")

    async def on_connect(self):
        print(f"Connecté sur {SERVER}")
        self.recreate_models()
        await self.join(CHANNEL)
        print(f"A rejoint {CHANNEL}")
        with open("tintin5.txt", "r") as f:
            self.tintin = f.read().splitlines()

    async def on_message(self, target, source, message):
        if not message or message[0] != "?" or source == self.nickname:
            return

        parsed = re.search(r"^.([a-zA-Z]+)(?: +(.*))?$", message)
        if not parsed:
            return

        command = parsed.group(1).lower()
        args = parsed.group(2)
        args = args.strip() if args else None

        if command in ("markov", "marchov"):
            if not args:
                return

            parsed = re.search(r"^([^ ]+)(?: +(.*))?$", args)
            if not parsed:
                return

            nick = parsed.group(1)
            if nick.strip() == "?":
                nicks = [m[0] for m in self.models.items() if m[1].size >= 10_000]
                normalized_nick = choice(nicks)
                nick = normalized_nick
            else:
                normalized_nick = normalize_nick(nick)
            prompt = parsed.group(2)
            prompt = prompt.strip() if prompt else None
            if normalized_nick not in self.models.keys():
                await self.message(target, f"{source}: aucun modèle trouvé pour {nick}")
                return

            model = self.models[normalized_nick]
            try:
                if prompt:
                    sentence = model.make_sentence_with_start(
                        beginning=prompt, tries=MARKOV_TRIES
                    )
                else:
                    sentence = model.make_sentence(tries=MARKOV_TRIES)
            except Exception:
                sentence = None

            if sentence:
                await self.message(target, f"{nick} dit: {sentence}")
            else:
                await self.message(
                    target,
                    f"{source}: impossible d'imiter {nick}{' avec ce prompt ' if prompt else ' '}(pas assez de contenu ?)",
                )
            return

        if command == "love":
            if not args:
                return

            parsed = re.search(r"^([^,]+),([^,]+)$", args)
            if not parsed:
                return
            lover_a = parsed.group(1).strip()
            lover_b = parsed.group(2).strip()
            normalized_lover_a = normalize_lover(lover_a)
            normalized_lover_b = normalize_lover(lover_b)
            normalized_lover_a, normalized_lover_b = sorted(
                (normalized_lover_a, normalized_lover_b)
            )
            query = f"{normalized_lover_a} {normalized_lover_b}"
            hash_ = md5(query.encode()).hexdigest()
            modulo = int(hash_, 16) % 101
            if normalized_lover_a == "barul" and normalized_lover_b == "biganon":
                modulo = 101
            await self.message(
                target,
                f"Compatibilité amoureuse entre {lover_a} et {lover_b} : {modulo}%",
            )

        if command == "tintin":
            if args:
                return
            sentence = choice(self.tintin)
            await self.message(target, f"{source}: {sentence}")

import pydle
import markovify
import re
from .secrets import *
from .utils import normalize_nick
from collections import defaultdict


class Marchov(pydle.Client):
    def __init__(self, *args, **kwargs):
        self.models = {}
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
            model = markovify.NewlineText("\n".join(messages[nick]), state_size=3)
            self.models[nick] = model
        print("Modèles recréés")

    async def on_connect(self):
        print(f"Connecté sur {SERVER}")
        self.recreate_models()
        await self.join(CHANNEL)
        print(f"A rejoint {CHANNEL}")

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

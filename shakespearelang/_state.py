from .errors import ShakespeareRuntimeError
from ._character import Character
from ._utils import normalize_name


class State:
    """State of a Shakespeare play execution context: variable values and who is on stage."""

    def __init__(self, personae):
        self.global_boolean = False
        self.characters = {}
        for persona in personae:
            character = Character.from_dramatis_persona(persona)
            if character.name in self.characters:
                raise ShakespeareRuntimeError(
                    f"{character.name} already initialized", parseinfo=persona.parseinfo
                )
            self.characters[character.name] = character
        self._characters_on_stage = {}
        self._characters_opposite = {}

    def __str__(self):
        return "\n".join(
            [f"global boolean = {self.global_boolean}", "on stage:"]
            + [f"  {c}" for _, c in self.characters.items() if c.on_stage]
            + ["off stage:"]
            + [f"  {c}" for _, c in self.characters.items() if not c.on_stage]
        )

    def enter_characters(self, characters):
        for character_name in characters:
            self.assert_character_off_stage(character_name)
        for character_name in characters:
            self._enter_character(character_name)

    def exeunt_characters(self, characters):
        for character_name in characters:
            self.assert_character_on_stage(character_name)
        for character_name in characters:
            self._exit_character(character_name)

    def exeunt_all(self):
        for character_name in list(self._characters_on_stage.keys()):
            self._exit_character(character_name)

    def exit_character(self, character_name):
        self.assert_character_on_stage(character_name)
        self._exit_character(character_name)

    def _enter_character(self, character_name):
        character = self.characters[character_name]
        character.on_stage = True
        self._characters_on_stage[character_name] = character
        self._update_opposites()

    def _exit_character(self, character_name):
        character = self.characters[character_name]
        character.on_stage = False
        del self._characters_on_stage[character_name]
        self._update_opposites()

    def _update_opposites(self):
        if len(self._characters_on_stage) != 2:
            self._characters_opposite = {}
        else:
            names = list(self._characters_on_stage.keys())
            self._characters_opposite[names[0]] = names[1]
            self._characters_opposite[names[1]] = names[0]

    def character_opposite(self, character):
        if character in self._characters_opposite:
            return self.characters[self._characters_opposite[character]]

        if character not in self._characters_on_stage:
            raise ShakespeareRuntimeError(f"{character.name} is not on stage!")
        elif len(self._characters_on_stage) > 2:
            raise ShakespeareRuntimeError("Ambiguous second-person pronoun")
        else:
            raise ShakespeareRuntimeError(f"{character} is talking to nobody!")

    def character_by_name(self, name):
        if name in self.characters:
            return self.characters[name]
        else:
            raise ShakespeareRuntimeError(f"{name} was not initialized!")

    def assert_character_on_stage(self, character_name):
        if character_name not in self._characters_on_stage:
            if character_name not in self.characters:
                raise ShakespeareRuntimeError(f"{character_name} was not initialized!")
            else:
                raise ShakespeareRuntimeError(f"{character_name} is not on stage!")

    def assert_character_off_stage(self, character_name):
        if character_name in self._characters_on_stage:
            raise ShakespeareRuntimeError(f"{character_name} is already on stage!")
        if character_name not in self.characters:
            raise ShakespeareRuntimeError(f"{character_name} was not initialized!")

from abc import ABC, abstractmethod

from automata import AFND
from automata.afnd import SpecialSymbol

__all__ = [
    "RegEx",
    "Empty",
    "Lambda",
    "Char",
    "Union",
    "Concat",
    "Star",
    "Plus"
]

class RegEx(ABC):
    """Clase abstracta para representar expresiones regulares."""
    
    def __init__(self):
        self._AFD = self.to_afnd().determinize().minimize()
        
    

    @abstractmethod
    def naive_match(self, word: str) -> bool:
        """
        Indica si la expresión regular acepta la cadena dada.
        Implementación recursiva, poco eficiente.
        """
        pass

    def match(self, word: str) -> bool:
        """Indica si la expresión regular acepta la cadena dada."""   
        miAFD = self._AFD
        return miAFD.match_string(word)

    @abstractmethod
    def to_afnd(self) -> AFND:
        """Convierte la expresión regular a un AFND."""
        pass 

    @abstractmethod
    def _atomic(self) -> bool:
        """
        (Interno) Indica si la expresión regular es atómica. Útil para
        implementar la función __str__.
        """
        pass


class Empty(RegEx):
    """Expresión regular que denota el lenguaje vacío (∅)."""
    def __init__(self):
         self._AFD = self.to_afnd().determinize().minimize()
    def naive_match(self, word: str):
        return False

    def to_afnd(self) -> AFND:
        M = AFND()
        M.add_state("q0", False)
        M.mark_initial_state("q0")
        M.add_state("q1", True)
        return M

    def _atomic(self):
        return True

    def __str__(self):
        return "∅"


class Lambda(RegEx):
    """Expresión regular que denota el lenguaje de la cadena vacía (Λ)."""
    def __init__(self):
         self._AFD = self.to_afnd().determinize().minimize()
    def naive_match(self, word: str):
        return word == ""
    
    def to_afnd(self) -> AFND:
        M = AFND()
        M.add_state("q0", True)
        M.mark_initial_state("q0")
        return M

    def _atomic(self):
        return True

    def __str__(self):
        return "λ"


class Char(RegEx):
    """Expresión regular que denota el lenguaje de un determinado carácter."""

    def __init__(self, char: str):
        assert len(char) == 1
        self.char = char
        self._AFD = self.to_afnd().determinize().minimize()

    def naive_match(self, word: str):
        return word == self.char

    def to_afnd(self) -> AFND:
        M = AFND()
        M.alphabet = set(self.char)
        M.add_state("q0", False)
        M.add_state("q1", True)
        M.mark_initial_state("q0")
        M.add_transition("q0","q1",self.char)

        M.normalize_states()
        return M


    def _atomic(self):
        return True

    def __str__(self):
        return self.char


class Concat(RegEx):
    """Expresión regular que denota la concatenación de dos expresiones regulares."""

    def __init__(self, exp1: RegEx, exp2: RegEx):
        self.exp1 = exp1
        self.exp2 = exp2
       
        self._AFD = self.to_afnd().determinize().minimize()

    def naive_match(self, word: str):
        for i in range(len(word) + 1):
            if self.exp1.naive_match(word[:i]) and self.exp2.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:     
        M1 = (self.exp1).to_afnd()
        M2 = (self.exp2).to_afnd()

        M = M1

        k = 0
        for q in M2.states:
            M2._rename_state(q, k) #"q"+str(k))
            k += 1

        M.states = M.states.union(M2.states)
        M.alphabet = M.alphabet.union(M2.alphabet)
        M.transitions = {**M.transitions, **M2.transitions}

        for f in M.final_states:
            M.add_transition(f, M2.initial_state, SpecialSymbol.Lambda)

        M.final_states = M2.final_states

        M = M.normalize_states()
        return M


    def _atomic(self):
        return False

    def __str__(self):
        return f"{f'({self.exp1})' if not self.exp1._atomic() else self.exp1}" \
            f"{f'({self.exp2})' if not self.exp2._atomic() else self.exp2}"


class Union(RegEx):
    """Expresión regular que denota la unión de dos expresiones regulares."""

    def __init__(self, exp1: RegEx, exp2: RegEx):
        self.exp1 = exp1
        self.exp2 = exp2
        self._AFD = self.to_afnd().determinize().minimize()

    def naive_match(self, word: str):
        return self.exp1.naive_match(word) or self.exp2.naive_match(word)

    def to_afnd(self) -> AFND:
        M1 = (self.exp1).to_afnd()
        M2 = (self.exp2).to_afnd()
        M = AFND()

        k = 0
        for q in M1.states:
            M1._rename_state(q, str(k))
            k += 1
    
        for q in M2.states:
            M2._rename_state(q, str(k))
            k += 1
            
        M.alphabet = M1.alphabet.union(M2.alphabet)
        M.states = M1.states.union(M2.states)
        M.final_states = M1.final_states.union(M2.final_states)

        M.transitions = {**M1.transitions, **M2.transitions}

        M.add_state("ini", False)
        M.mark_initial_state("ini")

        M.add_transition("ini", M1.initial_state, SpecialSymbol.Lambda)
        M.add_transition("ini", M2.initial_state, SpecialSymbol.Lambda)
        
        M= M.normalize_states()
        
        return M


    def _atomic(self):
        return False

    def __str__(self):
        return f"{f'({self.exp1})' if not self.exp1._atomic() else self.exp1}" \
            f"|{f'({self.exp2})' if not self.exp2._atomic() else self.exp2}"


class Star(RegEx):
    """Expresión regular que denota la clausura de Kleene de otra expresión regular."""

    def __init__(self, exp: RegEx):
        self.exp = exp
        self._AFD = self.to_afnd().determinize().minimize()

    def naive_match(self, word: str):
        if word == "" or self.exp.naive_match(word):
            return True
        for i in range(1, len(word) + 1):
            if self.exp.naive_match(word[:i]) and self.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:
        M1 = (self.exp).to_afnd()

        M = M1
        M.add_state("qA", False)
        M.mark_initial_state("qA")
        M.add_state("qB", False)

        M.add_transition("qA", (self.exp).to_afnd().initial_state, SpecialSymbol.Lambda)
        M.add_transition("qA", "qB", SpecialSymbol.Lambda)

        for q in M.final_states:
            M.add_transition(q, "qB", SpecialSymbol.Lambda)
            M.add_transition(q, (self.exp).to_afnd().initial_state, SpecialSymbol.Lambda)

        M.final_states = set(["qB"])

        M= M.normalize_states()
        return M
    
    def _atomic(self):
        return False

    def __str__(self):
        return f"({self.exp})*" if not self.exp._atomic() else f"{self.exp}*"


class Plus(RegEx):
    """Expresión regular que denota la clausura positiva de otra expresión regular."""

    def __init__(self, exp: RegEx):
        self.exp = exp
       
        self._AFD = self.to_afnd().determinize().minimize()

    def naive_match(self, word: str):
        if self.exp.naive_match(word):
            return True
        for i in range(1, len(word) + 1):
            if self.exp.naive_match(word[:i]) and self.naive_match(word[i:]):
                return True
        return False

    def to_afnd(self) -> AFND:
        M1 = (self.exp).to_afnd()

        M = M1
        M.add_state("qA", False)
        M.mark_initial_state("qA")
        M.add_state("qB", False)

        M.add_transition("qA", (self.exp).to_afnd().initial_state, SpecialSymbol.Lambda)

        for q in M.final_states:
            M.add_transition(q, "qB", SpecialSymbol.Lambda)
            M.add_transition(q, (self.exp).to_afnd().initial_state, SpecialSymbol.Lambda)

        M.final_states = set(["qB"])
        M= M.normalize_states()
        return M
    
    def _atomic(self) -> bool:
        return False

    def __str__(self):
        return f"({self.exp})+" if not self.exp._atomic() else f"{self.exp}+"


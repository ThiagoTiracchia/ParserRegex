from enum import Enum
from typing import Hashable, Union

from automata.af import AF
from automata.afd import AFD


__all__ = ["AFND"]


class SpecialSymbol(Enum):
    Lambda = "λ"


class AFND(AF):
    """Autómata finito no determinístico (con transiciones lambda)."""

    def add_transition(self, state1: Hashable, state2: Hashable, char: Union[str, SpecialSymbol]):
        """Agrega una transición al autómata."""
        if state1 not in self.states:
            raise ValueError(f"El estado {state1} no pertenece al autómata.")
        if state2 not in self.states:
            raise ValueError(f"El estado {state2} no pertenece al autómata.")
        if char not in self.transitions[state1]:
            self.transitions[state1][char] = set()
        self.transitions[state1][char].add(state2)
        if char is not SpecialSymbol.Lambda:
            self.alphabet.add(char)

# clasura se encarga de buscar todos los caminitos lambda que haya.
# Para ello, se usa una cola, y se mantiene un historial para no volver a encolar los estados para los cuales ya vimos la clausura lambda 
    def lambda_closure(self, p: set()) -> set():
        resHist = p
        res = list(p)
        kola = list(p)
        while len(kola) > 0:
            state = kola.pop()
            resHist.add(state)
                    
            if SpecialSymbol.Lambda in self.transitions[state]:
                res = res + list(self.transitions[state][SpecialSymbol.Lambda])
                kola = kola + list( self.transitions[state][SpecialSymbol.Lambda].difference(resHist) )                

        return set(res)
    
    def determinize(self) -> AFD:
        """Determiniza el autómata."""
                     
        def arreglar(algo: set()) -> set():
            return ''.join(sorted(list(algo)))
        
        miInicial = self.lambda_closure(set([self.initial_state]))
        nombre = arreglar(miInicial)

        res = AFD()
        res.alphabet = self.alphabet

        if len(miInicial.intersection(self.final_states)) != 0:
            res.add_state(nombre, True)
        else:
            res.add_state(nombre)
        res.mark_initial_state(nombre)


        kola = [miInicial]
        while len(kola) != 0:
            elemSet = kola.pop()
            
            for letra in self.alphabet:
                deltaLetra = set()
                for estado in elemSet:
                    if letra in self.transitions[estado]:
                        deltaLetra = deltaLetra.union(self.transitions[estado][letra])                
                miNuevoEstado = self.lambda_closure(deltaLetra)
                nombreNuevo = arreglar(miNuevoEstado)

                if nombreNuevo not in res.states:
                    kola.append(miNuevoEstado)
                    if len(miNuevoEstado.intersection(self.final_states)) != 0:
                        res.add_state(nombreNuevo, True)
                    else:
                        res.add_state(nombreNuevo)
                res.add_transition(arreglar(elemSet), nombreNuevo, letra)

        res.normalize_states()
        return res

    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        self.transitions[new_name] = self.transitions[old_name]
        del self.transitions[old_name]
        for state in self.transitions:
            for char in self.transitions[state]:
                if old_name in self.transitions[state][char]:
                    self.transitions[state][char].remove(old_name)
                    self.transitions[state][char].add(new_name)

    def _get_extended_alphabet(self) -> list[str]:
        """Obtiene el alfabeto extendido del autómata (incluyendo símbolos especiales)."""
        return list(self.alphabet) + [SpecialSymbol.Lambda]

    def _transitions_to_str(self, state: Hashable) -> dict[Hashable, str]:
        """Devuelve las transiciones de un estado para cada símbolo como string."""
        transitions = {}
        for char in self._get_extended_alphabet():
            if char in self.transitions[state]:
                transitions[char] = ",".join(self.transitions[state][char])
            else:
                transitions[char] = "-"
        return transitions



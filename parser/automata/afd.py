from typing import Hashable
from automata.af import AF

__all__ = ["AFD"]


class AFD(AF):
    """Autómata finito determinístico."""

    def add_transition(self, state1: Hashable, state2: Hashable, char: str):
        """Agrega una transición al autómata."""
        if state1 not in self.states:
            raise ValueError(f"El estado {state1} no pertenece al autómata.")
        if state2 not in self.states:
            raise ValueError(f"El estado {state2} no pertenece al autómata.")
        self.transitions[state1][char] = state2
        self.alphabet.add(char)

    def minimize(self):
        """Minimiza el autómata."""
        P = [self.final_states, self.states.difference(self.final_states)]
        W = [self.final_states, self.states.difference(self.final_states)]
        
        while (len(W) != 0 ) :
            A = W.pop()
            for c in self.alphabet:
                X = set()
                for state in self.states :
                    posible = self.transitions[state][c]
                    if (posible in A):
                        X.add(state)
                if (len(X) != 0) :         
                    for Y in P:
                        D = Y.difference(X)
                        I = X.intersection(Y)

                        if (((len(I) != 0) and len(D) != 0)):
                            P.remove(Y)
                            P.append(I)
                            P.append(D)
                        if (Y in W):
                            W.remove(Y)
                            W.append(I)
                            W.append(D)
                        elif (len(I) <= len(D)):
                            W.append(I)
                        else:
                            W.append(D)

        midicionario = {}
        
        i = 0

        miautomatito = AFD()

        for subconjunto in P:
            if (len(subconjunto) != 0 ) :
                for elemento in subconjunto:
                  midicionario[elemento] = i
                  if((elemento in self.final_states) and (i not in miautomatito.states)):
                      miautomatito.add_state(i,True)
                i = i+1 
       
        miautomatito.alphabet = self.alphabet
        for k in range(0,i) :
            if(k not in miautomatito.states):
                miautomatito.add_state(k,False)
        
        for subconjunto in P: 
            if (len(subconjunto) != 0): 
                miestado = subconjunto.pop()
                for c in miautomatito.alphabet :
                    nuevoEstado = midicionario[miestado]
                    estadoTransicion = midicionario[self.transitions[miestado][c]]
                    miautomatito.add_transition(nuevoEstado,estadoTransicion,c)
        miautomatito.mark_initial_state(midicionario[self.initial_state])
    
        return miautomatito

    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        self.transitions[new_name] = self.transitions[old_name]
        del self.transitions[old_name]
        for state in self.transitions:
            for char in self.transitions[state]:
                if self.transitions[state][char] == old_name:
                    self.transitions[state][char] = new_name

    def _get_extended_alphabet(self) -> list[str]:
        """Obtiene el alfabeto extendido del autómata (incluyendo símbolos especiales)."""
        return list(self.alphabet)

    def _transitions_to_str(self, state: Hashable) -> dict[Hashable, str]:
        """Devuelve las transiciones de un estado para cada símbolo como string."""
        transitions = {}
        for char in self._get_extended_alphabet():
            if char in self.transitions[state]:
                transitions[char] = self.transitions[state][char]
            else:
                transitions[char] = "-"
        return transitions

    def match_string(self, word):
        res = False
        estadoActual = self.initial_state
        
        for letra in word:
            if letra not in self.transitions[estadoActual]:
                return False #xq caso trampa no tiene rulitos a si mismo
            estadoActual = self.transitions[estadoActual][letra]
        
        if estadoActual in self.final_states:
            res = True

        return res

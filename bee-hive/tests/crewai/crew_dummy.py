# Dummy class for testing crewai loader
# SPDX-License-Identifier: Apache-2.0

class Crew:
    # TODO: kickoff actually takes & returns a dict[str,str]
    #def kickoff(inputs: dict[str, str]) -> str:
    def kickoff(self, inputs: dict[str,str]) -> str:

        print("Running kickoff method")
        print(inputs)
        return "OK"

class DummyCrew:
    def dummy_crew(self) -> Crew:
        print("Getting a Crew to return")
        return Crew()

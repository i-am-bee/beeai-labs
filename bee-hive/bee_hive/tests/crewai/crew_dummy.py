# Dummy class for testing crewai loader

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

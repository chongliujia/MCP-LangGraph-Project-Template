class Agent:
    """
    The Agent class represents a composite agent that utilizes the Model, Controller, and Planner.
    """
    def __init__(self, model, controller, planner):
        """
        Initialize the agent with model, controller, and planner.
        :param model: Model instance
        :param controller: Controller instance
        :param planner: Planner instance
        """
        self.model = model
        self.controller = controller
        self.planner = planner

    def act(self, task: str):
        """
        Perform the agent's action for a given task.
        :param task: Task to perform
        :return: Result of the agent's action
        """
        subtasks = self.planner.plan(task)
        results = []
        for subtask in subtasks:
            response = self.model.generate(subtask)
            result = self.controller.run(response)
            results.append(result)
        return results 
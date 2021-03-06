.. revealjs::

    .. revealjs:: Clean architecture, reusable components
       :subtitle: Stop starting from scratch

    .. revealjs:: How groundwork structures your code

        .. list-table::
            :header-rows: 0

            * - Application
              - Bundles plugins to an usable function set
            * - Plugins
              - Provides use case specific functions
            * - Patterns
              - Provides technical interfaces

        Example:

        .. image:: _static/example_plantuml.png

        .. rv_note::

            Diagram is generated using PlantUML.

    .. revealjs:: Example code

        Example: Application JenkinsGate

        .. rv_code::

            from groundwork import App

            class JenkinsGate:
                def __init__(self):
                    self.app = App()

                def start(self):
                    my_plugins = ["ViewDatabase", "ViewJenkinsData", "InformTeam"]
                    # Knowing plugin name is enough for activation
                    self.app.plugins.activate(my_plugins)

                    # Finally start the interface of choice, here a cli
                    self.app.commands.start_cli()

    .. revealjs:: Example code

        Example: Plugin ViewJenkinsData

        .. rv_code::

            from groundwork_database.patterns import GwSqlPattern
            from .patterns import MyJenkins

            class ViewJenkinsData(GwSqlPattern, MyJenkins):
                def __init__(self, app, **kwargs):
                    self.name = "ViewJenkinsData"
                    super().__init__(app, **kwargs)

                def activate(self):
                    self.db = self.databases.register("jenkins", "sqlite:///",
                                                      "database for jenkins data")

                    # Get and store first data already on activation
                    data = self.get_jenkins_data()
                    self.store_jenkins_data(data)

                def deactivate(self):
                    pass

                def get_jenkins_data(self):
                    data = self.jenkins.get_job("MyJob")
                    return data

                def store_jenkins_data(self, data)
                    self.db.add(data)
                    self.db.commit()

    .. revealjs:: Example code

        Example: Pattern MyJenkins

        .. rv_code::

            from groundwork.patterns import GwBasePattern

            class MyJenkins(GwBasePattern):
                def _init_(self, app, *args, **kwargs):
                    super().__init__(app, *args, **kwargs)
                    self.jenkins = Jenkins()

            class Jenkins:
                def get_job(self, job):
                    req =  requests.get("http://my_jenkins.com/{0}".format(job))
                    if req.status_code < 300:
                        return req.json()
                    else:
                        raise Exception("Ups, error happened!")
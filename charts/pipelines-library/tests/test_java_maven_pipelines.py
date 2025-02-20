from .helpers import helm_template


def test_java_maven_pipelines_gerrit():
    config = """
global:
  gitProvider: gerrit
  dockerRegistry:
    type: "ecr"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                assert f"gerrit-{buildtool}-{framework}-{cbtype}-review" in r["pipeline"]
                assert f"gerrit-{buildtool}-{framework}-{cbtype}-build-default" in r["pipeline"]
                assert f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp" in r["pipeline"]

                gerrit_review_pipeline = f"gerrit-{buildtool}-{framework}-{cbtype}-review"
                gerrit_build_pipeline_def = f"gerrit-{buildtool}-{framework}-{cbtype}-build-default"
                gerrit_build_pipeline_edp = f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp"

                rt = r["pipeline"][gerrit_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "fetch-target-branch" in rt[7]["name"]
                    assert "sonar-prepare-files" in rt[8]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[8]["taskRef"]["name"]
                    assert "sonar" in rt[9]["name"]
                    assert "build" in rt[10]["name"]
                    assert "dockerfile-lint" in rt[11]["name"]
                    assert "dockerbuild-verify" in rt[12]["name"]
                    assert "helm-lint" in rt[13]["name"]
                if cbtype == "lib":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "fetch-target-branch" in rt[5]["name"]
                    assert "sonar-prepare-files" in rt[6]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[6]["taskRef"]["name"]
                    assert "sonar" in rt[7]["name"]

                assert "gerrit-vote-success" in r["pipeline"][gerrit_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gerrit-vote-failure" in r["pipeline"][gerrit_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gerrit_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "gerrit-notify" in btd[1]["name"]
                assert "init-values" in btd[2]["name"]
                assert "get-version" in btd[3]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[3]["taskRef"]["name"]
                assert "update-build-number" == btd[4]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[5]["name"]
                    assert "sonar-cleanup" in btd[6]["name"]
                    assert "sast" in btd[7]["name"]
                    assert "compile" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "test" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "sonar" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "build" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[12]["name"]
                    assert "push" in btd[13]["name"]
                    assert buildtool == btd[13]["taskRef"]["name"]
                    assert "create-ecr-repository" in btd[14]["name"]
                    assert "kaniko-build" in btd[15]["name"]
                    assert "git-tag" in btd[16]["name"]
                    assert "update-cbis" in btd[17]["name"]
                else:
                    assert "sonar-cleanup" in btd[5]["name"]
                    assert "sast" in btd[6]["name"]
                    assert "compile" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "test" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "sonar" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "build" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[11]["name"]
                    assert "push" in btd[12]["name"]
                    assert buildtool == btd[12]["taskRef"]["name"]
                    assert "git-tag" in btd[13]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gerrit_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "gerrit-notify" in btedp[1]["name"]
                assert "init-values" in btedp[2]["name"]
                assert "get-version" in btedp[3]["name"]
                assert "get-version-edp" == btedp[3]["taskRef"]["name"]
                assert "update-build-number" in btedp[4]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[4]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[5]["name"]
                    assert "sonar-cleanup" in btedp[6]["name"]
                    assert "sast" in btedp[7]["name"]
                    assert "compile" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "test" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "sonar" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "build" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[12]["name"]
                    assert "push" in btedp[13]["name"]
                    assert buildtool == btedp[13]["taskRef"]["name"]
                    assert "create-ecr-repository" in btedp[14]["name"]
                    assert "kaniko-build" in btedp[15]["name"]
                    assert "git-tag" in btedp[16]["name"]
                    assert "update-cbis" in btedp[17]["name"]
                else:
                    assert "sonar-cleanup" in btedp[5]["name"]
                    assert "sast" in btedp[6]["name"]
                    assert "compile" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "test" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "sonar" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "build" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[11]["name"]
                    assert "push" in btedp[12]["name"]
                    assert buildtool == btedp[12]["taskRef"]["name"]
                    assert "git-tag" in btedp[13]["name"]
                assert "update-cbb" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_maven_pipelines_github():
    config = """
global:
  gitProvider: github
  dockerRegistry:
    type: "ecr"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                github_review_pipeline = f"github-{buildtool}-{framework}-{cbtype}-review"
                github_build_pipeline_def = f"github-{buildtool}-{framework}-{cbtype}-build-default"
                github_build_pipeline_edp = f"github-{buildtool}-{framework}-{cbtype}-build-edp"

                assert github_review_pipeline in r["pipeline"]
                assert github_build_pipeline_def in r["pipeline"]
                assert github_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][github_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "sonar" in rt[7]["name"]
                    assert "build" in rt[8]["name"]
                    assert "dockerfile-lint" in rt[9]["name"]
                    assert "dockerbuild-verify" in rt[10]["name"]
                    assert "helm-lint" in rt[11]["name"]
                if cbtype == "lib":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]

                assert "github-set-success-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][0]["name"]
                assert "github-set-failure-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][github_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" == btd[3]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[4]["name"]
                    assert "sast" in btd[5]["name"]
                    assert "compile" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "test" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "sonar" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "build" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[10]["name"]
                    assert "push" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "create-ecr-repository" in btd[12]["name"]
                    assert "kaniko-build" in btd[13]["name"]
                    assert "git-tag" in btd[14]["name"]
                    assert "update-cbis" in btd[15]["name"]
                if cbtype == "lib":
                    assert "sast" in btd[4]["name"]
                    assert "compile" in btd[5]["name"]
                    assert buildtool == btd[5]["taskRef"]["name"]
                    assert "test" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "sonar" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "build" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[9]["name"]
                    assert "push" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][github_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[3]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[4]["name"]
                    assert "sast" in btedp[5]["name"]
                    assert "compile" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "test" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "sonar" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "build" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[10]["name"]
                    assert "push" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "create-ecr-repository" in btedp[12]["name"]
                    assert "kaniko-build" in btedp[13]["name"]
                    assert "git-tag" in btedp[14]["name"]
                    assert "update-cbis" in btedp[15]["name"]
                if cbtype == "lib":
                    assert "sast" in btedp[4]["name"]
                    assert "compile" in btedp[5]["name"]
                    assert buildtool == btedp[5]["taskRef"]["name"]
                    assert "test" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "sonar" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "build" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[9]["name"]
                    assert "push" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_maven_pipelines_gitlab():
    config = """
global:
  gitProvider: gitlab
  dockerRegistry:
    type: "ecr"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                gitlab_review_pipeline = f"gitlab-{buildtool}-{framework}-{cbtype}-review"
                gitlab_build_pipeline_def = f"gitlab-{buildtool}-{framework}-{cbtype}-build-default"
                gitlab_build_pipeline_edp = f"gitlab-{buildtool}-{framework}-{cbtype}-build-edp"

                assert gitlab_review_pipeline in r["pipeline"]
                assert gitlab_build_pipeline_def in r["pipeline"]
                assert gitlab_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][gitlab_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "sonar" in rt[7]["name"]
                    assert "build" in rt[8]["name"]
                    assert "dockerfile-lint" in rt[9]["name"]
                    assert "dockerbuild-verify" in rt[10]["name"]
                    assert "helm-lint" in rt[11]["name"]
                if cbtype == "lib":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]

                assert "gitlab-set-success-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gitlab-set-failure-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gitlab_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" == btd[3]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[4]["name"]
                    assert "sast" in btd[5]["name"]
                    assert "compile" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "test" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "sonar" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "build" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[10]["name"]
                    assert "push" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "create-ecr-repository" in btd[12]["name"]
                    assert "kaniko-build" in btd[13]["name"]
                    assert "git-tag" in btd[14]["name"]
                    assert "update-cbis" in btd[15]["name"]
                if cbtype == "lib":
                    assert "sast" in btd[4]["name"]
                    assert "compile" in btd[5]["name"]
                    assert buildtool == btd[5]["taskRef"]["name"]
                    assert "test" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "sonar" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "build" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[9]["name"]
                    assert "push" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gitlab_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[3]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[4]["name"]
                    assert "sast" in btedp[5]["name"]
                    assert "compile" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "test" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "sonar" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "build" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[10]["name"]
                    assert "push" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "create-ecr-repository" in btedp[12]["name"]
                    assert "kaniko-build" in btedp[13]["name"]
                    assert "git-tag" in btedp[14]["name"]
                    assert "update-cbis" in btedp[15]["name"]
                if cbtype == "lib":
                    assert "sast" in btedp[4]["name"]
                    assert "compile" in btedp[5]["name"]
                    assert buildtool == btedp[5]["taskRef"]["name"]
                    assert "test" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "sonar" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "build" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[9]["name"]
                    assert "push" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_maven_pipelines_harbor_gerrit():
    config = """
global:
  gitProvider: gerrit
  dockerRegistry:
    type: "harbor"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                assert f"gerrit-{buildtool}-{framework}-{cbtype}-review" in r["pipeline"]
                assert f"gerrit-{buildtool}-{framework}-{cbtype}-build-default" in r["pipeline"]
                assert f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp" in r["pipeline"]

                gerrit_review_pipeline = f"gerrit-{buildtool}-{framework}-{cbtype}-review"
                gerrit_build_pipeline_def = f"gerrit-{buildtool}-{framework}-{cbtype}-build-default"
                gerrit_build_pipeline_edp = f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp"

                rt = r["pipeline"][gerrit_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "fetch-target-branch" in rt[7]["name"]
                    assert "sonar-prepare-files" in rt[8]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[8]["taskRef"]["name"]
                    assert "sonar" in rt[9]["name"]
                    assert "build" in rt[10]["name"]
                    assert "dockerfile-lint" in rt[11]["name"]
                    assert "dockerbuild-verify" in rt[12]["name"]
                    assert "helm-lint" in rt[13]["name"]
                if cbtype == "lib":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "fetch-target-branch" in rt[5]["name"]
                    assert "sonar-prepare-files" in rt[6]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[6]["taskRef"]["name"]
                    assert "sonar" in rt[7]["name"]

                assert "gerrit-vote-success" in r["pipeline"][gerrit_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gerrit-vote-failure" in r["pipeline"][gerrit_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gerrit_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "gerrit-notify" in btd[1]["name"]
                assert "init-values" in btd[2]["name"]
                assert "get-version" in btd[3]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[3]["taskRef"]["name"]
                assert "update-build-number" == btd[4]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[5]["name"]
                    assert "sonar-cleanup" in btd[6]["name"]
                    assert "sast" in btd[7]["name"]
                    assert "compile" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "test" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "sonar" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "build" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[12]["name"]
                    assert "push" in btd[13]["name"]
                    assert buildtool == btd[13]["taskRef"]["name"]
                    assert "kaniko-build" in btd[14]["name"]
                    assert "git-tag" in btd[15]["name"]
                    assert "update-cbis" in btd[16]["name"]
                else:
                    assert "sonar-cleanup" in btd[5]["name"]
                    assert "sast" in btd[6]["name"]
                    assert "compile" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "test" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "sonar" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "build" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[11]["name"]
                    assert "push" in btd[12]["name"]
                    assert buildtool == btd[12]["taskRef"]["name"]
                    assert "git-tag" in btd[13]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gerrit_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "gerrit-notify" in btedp[1]["name"]
                assert "init-values" in btedp[2]["name"]
                assert "get-version" in btedp[3]["name"]
                assert "get-version-edp" == btedp[3]["taskRef"]["name"]
                assert "update-build-number" in btedp[4]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[4]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[5]["name"]
                    assert "sonar-cleanup" in btedp[6]["name"]
                    assert "sast" in btedp[7]["name"]
                    assert "compile" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "test" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "sonar" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "build" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[12]["name"]
                    assert "push" in btedp[13]["name"]
                    assert buildtool == btedp[13]["taskRef"]["name"]
                    assert "kaniko-build" in btedp[14]["name"]
                    assert "git-tag" in btedp[15]["name"]
                    assert "update-cbis" in btedp[16]["name"]
                else:
                    assert "sonar-cleanup" in btedp[5]["name"]
                    assert "sast" in btedp[6]["name"]
                    assert "compile" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "test" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "sonar" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "build" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[11]["name"]
                    assert "push" in btedp[12]["name"]
                    assert buildtool == btedp[12]["taskRef"]["name"]
                    assert "git-tag" in btedp[13]["name"]
                assert "update-cbb" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_maven_pipelines_harbor_github():
    config = """
global:
  gitProvider: github
  dockerRegistry:
    type: "harbor"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                github_review_pipeline = f"github-{buildtool}-{framework}-{cbtype}-review"
                github_build_pipeline_def = f"github-{buildtool}-{framework}-{cbtype}-build-default"
                github_build_pipeline_edp = f"github-{buildtool}-{framework}-{cbtype}-build-edp"

                assert github_review_pipeline in r["pipeline"]
                assert github_build_pipeline_def in r["pipeline"]
                assert github_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][github_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "sonar" in rt[7]["name"]
                    assert "build" in rt[8]["name"]
                    assert "dockerfile-lint" in rt[9]["name"]
                    assert "dockerbuild-verify" in rt[10]["name"]
                    assert "helm-lint" in rt[11]["name"]
                if cbtype == "lib":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]

                assert "github-set-success-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][0]["name"]
                assert "github-set-failure-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][github_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[4]["name"]
                    assert "sast" in btd[5]["name"]
                    assert "compile" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "test" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "sonar" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "build" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[10]["name"]
                    assert "push" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "kaniko-build" in btd[12]["name"]
                    assert "git-tag" in btd[13]["name"]
                    assert "update-cbis" in btd[14]["name"]
                if cbtype == "lib":
                    assert "sast" in btd[4]["name"]
                    assert "compile" in btd[5]["name"]
                    assert buildtool == btd[5]["taskRef"]["name"]
                    assert "test" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "sonar" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "build" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[9]["name"]
                    assert "push" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][github_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[3]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[4]["name"]
                    assert "sast" in btedp[5]["name"]
                    assert "compile" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "test" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "sonar" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "build" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[10]["name"]
                    assert "push" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "kaniko-build" in btedp[12]["name"]
                    assert "git-tag" in btedp[13]["name"]
                    assert "update-cbis" in btedp[14]["name"]
                if cbtype == "lib":
                    assert "sast" in btedp[4]["name"]
                    assert "compile" in btedp[5]["name"]
                    assert buildtool == btedp[5]["taskRef"]["name"]
                    assert "test" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "sonar" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "build" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[9]["name"]
                    assert "push" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_maven_pipelines_harbor_gitlab():
    config = """
global:
  gitProvider: gitlab
  dockerRegistry:
    type: "harbor"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['maven']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                gitlab_review_pipeline = f"gitlab-{buildtool}-{framework}-{cbtype}-review"
                gitlab_build_pipeline_def = f"gitlab-{buildtool}-{framework}-{cbtype}-build-default"
                gitlab_build_pipeline_edp = f"gitlab-{buildtool}-{framework}-{cbtype}-build-edp"

                assert gitlab_review_pipeline in r["pipeline"]
                assert gitlab_build_pipeline_def in r["pipeline"]
                assert gitlab_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][gitlab_review_pipeline]["spec"]["tasks"]
                if cbtype == "app":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "get-maven-module" in rt[4]["name"]
                    assert "compile" in rt[5]["name"]
                    assert "test" in rt[6]["name"]
                    assert "sonar" in rt[7]["name"]
                    assert "build" in rt[8]["name"]
                    assert "dockerfile-lint" in rt[9]["name"]
                    assert "dockerbuild-verify" in rt[10]["name"]
                    assert "helm-lint" in rt[11]["name"]
                if cbtype == "lib":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]

                assert "gitlab-set-success-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gitlab-set-failure-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gitlab_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btd[4]["name"]
                    assert "sast" in btd[5]["name"]
                    assert "compile" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "test" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "sonar" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "build" in btd[9]["name"]
                    assert buildtool == btd[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[10]["name"]
                    assert "push" in btd[11]["name"]
                    assert buildtool == btd[11]["taskRef"]["name"]
                    assert "kaniko-build" in btd[12]["name"]
                    assert "git-tag" in btd[13]["name"]
                    assert "update-cbis" in btd[14]["name"]
                if cbtype == "lib":
                    assert "sast" in btd[4]["name"]
                    assert "compile" in btd[5]["name"]
                    assert buildtool == btd[5]["taskRef"]["name"]
                    assert "test" in btd[6]["name"]
                    assert buildtool == btd[6]["taskRef"]["name"]
                    assert "sonar" in btd[7]["name"]
                    assert buildtool == btd[7]["taskRef"]["name"]
                    assert "build" in btd[8]["name"]
                    assert buildtool == btd[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btd[9]["name"]
                    assert "push" in btd[10]["name"]
                    assert buildtool == btd[10]["taskRef"]["name"]
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gitlab_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["taskRef"]["name"]
                assert f"update-build-number-{buildtool}" == btedp[3]["taskRef"]["name"]
                if cbtype == "app":
                    assert "get-maven-module" in btedp[4]["name"]
                    assert "sast" in btedp[5]["name"]
                    assert "compile" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "test" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "sonar" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "build" in btedp[9]["name"]
                    assert buildtool == btedp[9]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[10]["name"]
                    assert "push" in btedp[11]["name"]
                    assert buildtool == btedp[11]["taskRef"]["name"]
                    assert "kaniko-build" in btedp[12]["name"]
                    assert "git-tag" in btedp[13]["name"]
                    assert "update-cbis" in btedp[14]["name"]
                if cbtype == "lib":
                    assert "sast" in btedp[4]["name"]
                    assert "compile" in btedp[5]["name"]
                    assert buildtool == btedp[5]["taskRef"]["name"]
                    assert "test" in btedp[6]["name"]
                    assert buildtool == btedp[6]["taskRef"]["name"]
                    assert "sonar" in btedp[7]["name"]
                    assert buildtool == btedp[7]["taskRef"]["name"]
                    assert "build" in btedp[8]["name"]
                    assert buildtool == btedp[8]["taskRef"]["name"]
                    assert "get-nexus-repository-url" in btedp[9]["name"]
                    assert "push" in btedp[10]["name"]
                    assert buildtool == btedp[10]["taskRef"]["name"]
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][1]["name"]

from .helpers import helm_template


def test_java_gradle_pipelines_gerrit():
    config = """
global:
  gitProvider: gerrit
  dockerRegistry:
    type: "ecr"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                gerrit_review_pipeline = f"gerrit-{buildtool}-{framework}-{cbtype}-review"
                gerrit_build_pipeline_def = f"gerrit-{buildtool}-{framework}-{cbtype}-build-default"
                gerrit_build_pipeline_edp = f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp"

                assert gerrit_review_pipeline in r["pipeline"]
                assert gerrit_build_pipeline_def in r["pipeline"]
                assert gerrit_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][gerrit_review_pipeline]["spec"]["tasks"]
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
                if cbtype == "app":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "fetch-target-branch" in rt[6]["name"]
                    assert "sonar-prepare-files" in rt[7]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[7]["taskRef"]["name"]
                    assert "sonar" in rt[8]["name"]
                    assert "build" in rt[9]["name"]
                    assert "dockerfile-lint" in rt[10]["name"]
                    assert "dockerbuild-verify" in rt[11]["name"]
                    assert "helm-lint" in rt[12]["name"]

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
                assert "update-build-number" in btd[4]["name"]
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
                if cbtype == "app":
                    assert "create-ecr-repository" in btd[13]["name"]
                    assert "kaniko-build" in btd[14]["name"]
                    assert "git-tag" in btd[15]["name"]
                    assert "update-cbis" in btd[16]["name"]
                else:
                    assert "git-tag" in btd[13]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gerrit_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "gerrit-notify" in btedp[1]["name"]
                assert "init-values" in btedp[2]["name"]
                assert "get-version" in btedp[3]["name"]
                assert "get-version-edp" == btedp[3]["taskRef"]["name"]
                idx = 3
                # we have update-build-number only for gradle
                if buildtool == "gradle":
                    assert "update-build-number" in btedp[4]["taskRef"]["name"]
                    assert f"update-build-number-{buildtool}" == btedp[4]["taskRef"]["name"]
                    idx = 4
                assert "sonar-cleanup" in btedp[idx+1]["name"]
                assert "sast" in btedp[idx+2]["name"]
                assert "compile" in btedp[idx+3]["name"]
                assert buildtool == btedp[idx+3]["taskRef"]["name"]
                assert "test" in btedp[idx+4]["name"]
                assert buildtool == btedp[idx+4]["taskRef"]["name"]
                assert "sonar" in btedp[idx+5]["name"]
                assert buildtool == btedp[idx+5]["taskRef"]["name"]
                assert "build" in btedp[idx+6]["name"]
                assert buildtool == btedp[idx+6]["taskRef"]["name"]
                assert "get-nexus-repository-url" in btedp[idx+7]["name"]
                assert "push" in btedp[idx+8]["name"]
                assert buildtool == btedp[idx+8]["taskRef"]["name"]
                if cbtype == "app":
                    assert "create-ecr-repository" in btedp[idx+9]["name"]
                    assert "kaniko-build" in btedp[idx+10]["name"]
                    assert "git-tag" in btedp[idx+11]["name"]
                    assert "update-cbis" in btedp[idx+12]["name"]
                else:
                    assert "git-tag" in btedp[idx+9]["name"]
                assert "update-cbb" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_gradle_pipelines_github():
    config = """
global:
  gitProvider: github
  dockerRegistry:
    type: "ecr"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                github_review_pipeline = f"github-{buildtool}-{framework}-{cbtype}-review"
                github_build_pipeline_def = f"github-{buildtool}-{framework}-{cbtype}-build-default"
                github_build_pipeline_edp = f"github-{buildtool}-{framework}-{cbtype}-build-edp"

                assert github_review_pipeline in r["pipeline"]
                assert github_build_pipeline_def in r["pipeline"]
                assert github_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][github_review_pipeline]["spec"]["tasks"]
                if cbtype == "lib":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]
                if cbtype == "app":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "sonar" in rt[6]["name"]
                    assert "build" in rt[7]["name"]
                    assert "dockerfile-lint" in rt[8]["name"]
                    assert "dockerbuild-verify" in rt[9]["name"]
                    assert "helm-lint" in rt[10]["name"]

                assert "github-set-success-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][0]["name"]
                assert "github-set-failure-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][github_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
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
                if cbtype == "app":
                    assert "create-ecr-repository" in btd[11]["name"]
                    assert "kaniko-build" in btd[12]["name"]
                    assert "git-tag" in btd[13]["name"]
                    assert "update-cbis" in btd[14]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][github_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["name"]
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
                if cbtype == "app":
                    assert "create-ecr-repository" in btedp[11]["name"]
                    assert "kaniko-build" in btedp[12]["name"]
                    assert "git-tag" in btedp[13]["name"]
                    assert "update-cbis" in btedp[14]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_gradle_pipelines_gitlab():
    config = """
global:
  gitProvider: gitlab
  dockerRegistry:
    type: "ecr"
    """
    r = helm_template(config)
    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:
                gitlab_review_pipeline = f"gitlab-{buildtool}-{framework}-{cbtype}-review"
                gitlab_build_pipeline_def = f"gitlab-{buildtool}-{framework}-{cbtype}-build-default"
                gitlab_build_pipeline_edp = f"gitlab-{buildtool}-{framework}-{cbtype}-build-edp"
                assert gitlab_review_pipeline in r["pipeline"]
                assert gitlab_build_pipeline_def in r["pipeline"]
                assert gitlab_build_pipeline_edp in r["pipeline"]
                rt = r["pipeline"][gitlab_review_pipeline]["spec"]["tasks"]
                if cbtype == "lib":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]
                if cbtype == "app":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "sonar" in rt[6]["name"]
                    assert "build" in rt[7]["name"]
                    assert "dockerfile-lint" in rt[8]["name"]
                    assert "dockerbuild-verify" in rt[9]["name"]
                    assert "helm-lint" in rt[10]["name"]
                assert "gitlab-set-success-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gitlab-set-failure-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gitlab_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
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
                if cbtype == "app":
                    assert "create-ecr-repository" in btd[11]["name"]
                    assert "kaniko-build" in btd[12]["name"]
                    assert "git-tag" in btd[13]["name"]
                    assert "update-cbis" in btd[14]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gitlab_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["name"]
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
                if cbtype == "app":
                    assert "create-ecr-repository" in btedp[11]["name"]
                    assert "kaniko-build" in btedp[12]["name"]
                    assert "git-tag" in btedp[13]["name"]
                    assert "update-cbis" in btedp[14]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_gradle_pipelines_harbor_gerrit():
    config = """
global:
  gitProvider: gerrit
  dockerRegistry:
    type: "harbor"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                gerrit_review_pipeline = f"gerrit-{buildtool}-{framework}-{cbtype}-review"
                gerrit_build_pipeline_def = f"gerrit-{buildtool}-{framework}-{cbtype}-build-default"
                gerrit_build_pipeline_edp = f"gerrit-{buildtool}-{framework}-{cbtype}-build-edp"

                assert gerrit_review_pipeline in r["pipeline"]
                assert gerrit_build_pipeline_def in r["pipeline"]
                assert gerrit_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][gerrit_review_pipeline]["spec"]["tasks"]
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
                if cbtype == "app":
                    assert "fetch-repository" in rt[0]["name"]
                    assert "gerrit-notify" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "fetch-target-branch" in rt[6]["name"]
                    assert "sonar-prepare-files" in rt[7]["name"]
                    assert f"sonar-prepare-files-{buildtool}" == rt[7]["taskRef"]["name"]
                    assert "sonar" in rt[8]["name"]
                    assert "build" in rt[9]["name"]
                    assert "dockerfile-lint" in rt[10]["name"]
                    assert "dockerbuild-verify" in rt[11]["name"]
                    assert "helm-lint" in rt[12]["name"]

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
                assert "update-build-number" in btd[4]["name"]
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
                if cbtype == "app":
                    assert "kaniko-build" in btd[13]["name"]
                    assert "git-tag" in btd[14]["name"]
                    assert "update-cbis" in btd[15]["name"]
                else:
                    assert "git-tag" in btd[13]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gerrit_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "gerrit-notify" in btedp[1]["name"]
                assert "init-values" in btedp[2]["name"]
                assert "get-version" in btedp[3]["name"]
                assert "get-version-edp" == btedp[3]["taskRef"]["name"]
                idx = 3
                # we have update-build-number only for gradle
                if buildtool == "gradle":
                    assert "update-build-number" in btedp[4]["taskRef"]["name"]
                    assert f"update-build-number-{buildtool}" == btedp[4]["taskRef"]["name"]
                    idx = 4

                assert "sonar-cleanup" in btedp[idx+1]["name"]
                assert "sast" in btedp[idx+2]["name"]
                assert "compile" in btedp[idx+3]["name"]
                assert buildtool == btedp[idx+3]["taskRef"]["name"]
                assert "test" in btedp[idx+4]["name"]
                assert buildtool == btedp[idx+4]["taskRef"]["name"]
                assert "sonar" in btedp[idx+5]["name"]
                assert buildtool == btedp[idx+5]["taskRef"]["name"]
                assert "build" in btedp[idx+6]["name"]
                assert buildtool == btedp[idx+6]["taskRef"]["name"]
                assert "get-nexus-repository-url" in btedp[idx+7]["name"]
                assert "push" in btedp[idx+8]["name"]
                assert buildtool == btedp[idx+8]["taskRef"]["name"]
                if cbtype == "app":
                    assert "kaniko-build" in btedp[idx+9]["name"]
                    assert "git-tag" in btedp[idx+10]["name"]
                    assert "update-cbis" in btedp[idx+11]["name"]
                else:
                    assert "git-tag" in btedp[idx+9]["name"]
                assert "update-cbb" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gerrit_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_gradle_pipelines_harbor_github():
    config = """
global:
  gitProvider: github
  dockerRegistry:
    type: "harbor"
    """

    r = helm_template(config)

    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:

                github_review_pipeline = f"github-{buildtool}-{framework}-{cbtype}-review"
                github_build_pipeline_def = f"github-{buildtool}-{framework}-{cbtype}-build-default"
                github_build_pipeline_edp = f"github-{buildtool}-{framework}-{cbtype}-build-edp"

                assert github_review_pipeline in r["pipeline"]
                assert github_build_pipeline_def in r["pipeline"]
                assert github_build_pipeline_edp in r["pipeline"]

                rt = r["pipeline"][github_review_pipeline]["spec"]["tasks"]
                if cbtype == "lib":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]
                if cbtype == "app":
                    assert "github-set-pending-status" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "sonar" in rt[6]["name"]
                    assert "build" in rt[7]["name"]
                    assert "dockerfile-lint" in rt[8]["name"]
                    assert "dockerbuild-verify" in rt[9]["name"]
                    assert "helm-lint" in rt[10]["name"]

                assert "github-set-success-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][0]["name"]
                assert "github-set-failure-status" in r["pipeline"][github_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][github_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
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
                if cbtype == "app":
                    assert "kaniko-build" in btd[11]["name"]
                    assert "git-tag" in btd[12]["name"]
                    assert "update-cbis" in btd[13]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][github_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["name"]
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
                if cbtype == "app":
                    assert "kaniko-build" in btedp[11]["name"]
                    assert "git-tag" in btedp[12]["name"]
                    assert "update-cbis" in btedp[13]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][github_build_pipeline_edp]["spec"]["finally"][1]["name"]


def test_java_gradle_pipelines_harbor_gitlab():
    config = """
global:
  gitProvider: gitlab
  dockerRegistry:
    type: "harbor"
    """
    r = helm_template(config)
    # ensure pipelines have proper steps
    for buildtool in ['gradle']:
        for framework in ['java8', 'java11', 'java17']:
            for cbtype in ['app', 'lib']:
                gitlab_review_pipeline = f"gitlab-{buildtool}-{framework}-{cbtype}-review"
                gitlab_build_pipeline_def = f"gitlab-{buildtool}-{framework}-{cbtype}-build-default"
                gitlab_build_pipeline_edp = f"gitlab-{buildtool}-{framework}-{cbtype}-build-edp"
                assert gitlab_review_pipeline in r["pipeline"]
                assert gitlab_build_pipeline_def in r["pipeline"]
                assert gitlab_build_pipeline_edp in r["pipeline"]
                rt = r["pipeline"][gitlab_review_pipeline]["spec"]["tasks"]
                if cbtype == "lib":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "compile" in rt[3]["name"]
                    assert "test" in rt[4]["name"]
                    assert "sonar" in rt[5]["name"]
                if cbtype == "app":
                    assert "report-pipeline-start-to-gitlab" in rt[0]["name"]
                    assert "fetch-repository" in rt[1]["name"]
                    assert "init-values" in rt[2]["name"]
                    assert "helm-docs" in rt[3]["name"]
                    assert "compile" in rt[4]["name"]
                    assert "test" in rt[5]["name"]
                    assert "sonar" in rt[6]["name"]
                    assert "build" in rt[7]["name"]
                    assert "dockerfile-lint" in rt[8]["name"]
                    assert "dockerbuild-verify" in rt[9]["name"]
                    assert "helm-lint" in rt[10]["name"]
                assert "gitlab-set-success-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][0]["name"]
                assert "gitlab-set-failure-status" in r["pipeline"][gitlab_review_pipeline]["spec"]["finally"][1]["name"]

                # build with default versioning
                btd = r["pipeline"][gitlab_build_pipeline_def]["spec"]["tasks"]
                assert "fetch-repository" in btd[0]["name"]
                assert "init-values" in btd[1]["name"]
                assert "get-version" in btd[2]["name"]
                # ensure we have default versioning
                assert f"get-version-default" == btd[2]["taskRef"]["name"]
                assert "update-build-number" in btd[3]["name"]
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
                if cbtype == "app":
                    assert "kaniko-build" in btd[11]["name"]
                    assert "git-tag" in btd[12]["name"]
                    assert "update-cbis" in btd[13]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btd[11]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_def]["spec"]["finally"][0]["name"]

                # build with edp versioning
                btedp = r["pipeline"][gitlab_build_pipeline_edp]["spec"]["tasks"]
                assert "fetch-repository" in btedp[0]["name"]
                assert "init-values" in btedp[1]["name"]
                assert "get-version" in btedp[2]["name"]
                assert "get-version-edp" == btedp[2]["taskRef"]["name"]
                assert "update-build-number" in btedp[3]["name"]
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
                if cbtype == "app":
                    assert "kaniko-build" in btedp[11]["name"]
                    assert "git-tag" in btedp[12]["name"]
                    assert "update-cbis" in btedp[13]["name"]
                if cbtype == "lib":
                    assert "git-tag" in btedp[11]["name"]
                assert "update-cbb" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][0]["name"]
                assert "push-to-jira" in r["pipeline"][gitlab_build_pipeline_edp]["spec"]["finally"][1]["name"]

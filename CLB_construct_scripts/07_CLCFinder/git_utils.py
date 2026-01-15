import subprocess

def git_checkout(repo_path, commit_sha):
    # 指定要执行的git命令
    git_command = ["git", "checkout", "-f",commit_sha]

    try:
        # 切换到指定路径并执行git命令
        result = subprocess.run(git_command, cwd=repo_path, text=True, capture_output=True, check=True,encoding='utf-8',errors='ignore')

        # 输出结果
        # print("------git checkout命令:stdout:", result.stdout)
        print("------git checkout命令:stderr:", result.stderr)

    except subprocess.CalledProcessError as e:
        print("-异常,git命令- Error occurred during git checkout:")
        print(e.stderr)
        print("-异常,git命令- Return code:", e.returncode)
import docker


def build_docker_image(client, file_path, repository, tag):
    try:
        image, build_logs = client.images.build(path=file_path, dockerfile='Dockerfile', tag=f"{repository}:{tag}")

        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())

        return image
    except docker.errors.BuildError as e:
        print(f"Build failed: {e}")
        return None


def push_docker_image(client, repository, tag):
    try:
        push_result = client.images.push(repository, tag=tag)

        for line in push_result:
            print(line, end='')

    except docker.errors.APIError as e:
        print(f"Push failed: {e}")


def main():
    # Initialize the Docker client
    client = docker.from_env()

    file_path = input("Enter the path to your Dockerfile: ")
    repository = input("Enter your Repository and Image name: ")
    tag = input("Enter your Image tag: ")

    image = build_docker_image(client, file_path, repository, tag)

    if image:
        print(f"Build successful for image: {repository}:{tag}")

        # Confirmation
        user_input = input(
            f"Would you like to push image {repository}:{tag} to the repository {repository}? (yes/no): ")

        if user_input.lower() in ['yes', 'y']:
            push_docker_image(client, repository, tag)
        else:
            print("Okay, the image was built but not pushed.")
    else:
        print("Build failed, exiting.")


main()

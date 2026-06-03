from setuptools import find_packages, setup

package_name = "casbot2_py_demo"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="casbot2-dev",
    maintainer_email="maintainer@example.com",
    description="CASBOT2 Python secondary development demos",
    license="MIT",
    entry_points={
        "console_scripts": [
            "control_demo = casbot2_py_demo.control_demo:main",
            "service_mode_demo = casbot2_py_demo.service_mode_demo:main",
            "debug_joint_demo = casbot2_py_demo.debug_joint_demo:main",
            "monitor_topics_demo = casbot2_py_demo.monitor_topics_demo:main",
            "action_voice_demo = casbot2_py_demo.action_voice_demo:main",
        ],
    },
)

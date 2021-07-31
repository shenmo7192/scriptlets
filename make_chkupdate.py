#!/usr/bin/python3

import requests
import sys
import os

def main():
    package_name = sys.argv[1]
    r = requests.get("https://release-monitoring.org/api/projects/?pattern={}".format(package_name))
    d = r.json()
    print("Anitya:")
    if d["total"] != 0:
        for i in d["projects"]:
            print("Name: {}, Lastest Version: {}, CHKUPDATE: anitya::id={}".format(i["name"], i["stable_versions"][0] if len(i["stable_versions"]) != 0 else "None", i["id"]))
    srcs = []
    print("Github:")
    package_path = search_package_path(package_name)
    with open("{}/spec".format(package_path)) as f:
        spec = f.readlines()
        for i in spec:
            if "SRCS=" in i:
                if len(i.split("::")) > 1:
                        srcs += i.split("::")[1][:-1].split('\n')
                else:
                        srcs += i[:-1].split('\n')
    for i in srcs:
        if "github" in i:
            split_i = i.split("/")
            print("CHKUPDATE: github::repo={}/{}".format(split_i[3], split_i[4]))


def search_package_path(package_name: str) -> str:
    with os.scandir(".") as dir1:
        for section in dir1:
            if section.is_dir() and not section.name.startswith('.'):
                with os.scandir(section) as dir2:
                    for package in dir2:
                        if package.name == package_name and package.is_dir() and os.path.isdir(
                                os.path.join(package, "autobuild")):
                            return package.path[2:]
                        # search subpackage, like arch-install-scripts/01-genfstab
                        path = package
                        if os.path.isdir(path) and section.name != "groups":
                            with os.scandir(path) as dir3:
                                for subpackage in dir3:
                                    if subpackage.name != "autobuild" and subpackage.is_dir():
                                        try:
                                            with open(os.path.join(subpackage, "defines"), "r") as f:
                                                defines = f.readlines()
                                        except:
                                            with open(os.path.join(subpackage, "autobuild/defines"), "r") as f:
                                                defines = f.readlines()
                                        finally:
                                            for line in defines:
                                                if "PKGNAME=" in line and package_name in line:
                                                    return package.path[2:]

if __name__ == "__main__":
    main()

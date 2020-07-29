from conans import CMake, ConanFile, tools
import os

# based on https://github.com/Yevgnen/conan-armadillo

class ArmadilloConan(ConanFile):
    name = "armadillo"
    version = "8.500.1"
    license = "Apache License 2.0"
    url = "http://arma.sourceforge.net/"
    description = "C++ linear algebra library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "ARMA_USE_LAPACK": [True, False],
               "ARMA_USE_BLAS": [True, False]}
    default_options = "shared=False", "ARMA_USE_LAPACK=False", "ARMA_USE_BLAS=False"
    generators = "cmake"
    source_folder_name = ("armadillo-%s" % version)
    source_tarxz_file = ("%s.tar.xz.old" % source_folder_name)
    source_tar_file = ("%s.tar" % source_folder_name)

    def source(self):
        tools.download(("http://sourceforge.net/projects/arma/files/%s" % self.source_tarxz_file),
                       self.source_tarxz_file)
        self.run("tar -xvf %s" % self.source_tarxz_file)
        os.unlink(self.source_tarxz_file)
        os.rename(self.source_folder_name, "sources")

    def system_requirements(self):
        pack_names = []
        if self.options.ARMA_USE_LAPACK:
            pack_names.append("liblapack-dev")
        if self.options.ARMA_USE_BLAS:
            pack_names.append("libopenblas-dev")
        if pack_names:
            installer = tools.SystemPackageTool()
            installer.update()  # Update the package database
            installer.install(" ".join(pack_names))  # Install the package

    def build(self):
        if not self.options.ARMA_USE_LAPACK:
            tools.replace_in_file(file_path="sources/include/armadillo_bits/config.hpp",
                                  search="#define ARMA_USE_LAPACK",
                                  replace="//#define ARMA_USE_LAPACK")

        if not self.options.ARMA_USE_BLAS:
            tools.replace_in_file(file_path="sources/include/armadillo_bits/config.hpp",
                                  search="#define ARMA_USE_BLAS",
                                  replace="//#define ARMA_USE_BLAS")

        cmake = CMake(self)
        cmake.configure(source_dir="sources")
        cmake.build()

    def package(self):
        self.copy("armadillo", dst="include", src="sources/include")
        self.copy("*.hpp", dst="include/armadillo_bits",
                  src="sources/include/armadillo_bits")
        self.copy("*armadillo.lib", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.so.*", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["armadillo"]
        if self.options.ARMA_USE_LAPACK:
            self.cpp_info.libs.append("lapack")
        if self.options.ARMA_USE_BLAS:
            self.cpp_info.libs.append("openblas")
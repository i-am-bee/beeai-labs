class Maestro < Formula
  desc "A multi-agent platform with the vision to facilitate deploy and run AI agents"
  homepage "https://github.com/IBM/maestro"
  url "https://github.com/IBM/maestro/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "f89b59e5b95dcb9219b4420487143249802e5dd2dc00bd71bf39e6fbc1a73233"
  license "Apache-2.0"
  head "https://github.com/IBM/maestro.git", branch: "main"

  depends_on "python@3.11"
  depends_on "poetry"

  def install
    system "poetry", "install", "--no-dev", "--no-interaction"
    system "poetry", "build"
    
    # Install the package
    system "pip3", "install", "--prefix=#{prefix}", "dist/maestro-0.1.0.tar.gz"
    
    # Create a wrapper script
    (bin/"maestro").write <<~EOS
      #!/bin/bash
      exec "#{libexec}/bin/maestro" "$@"
    EOS
    chmod 0755, bin/"maestro"
  end

  test do
    system "#{bin}/maestro", "--version"
  end
end 
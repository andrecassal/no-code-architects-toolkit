# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # pkgs.go
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python312Packages.pillow
    # pkgs.nodejs_20
    # pkgs.nodePackages.nodemon
    # pkgs.python311Packages.Flask
    # pkgs.python311Packages.Werkzeug
    # pkgs.python311Packages.requests
    # pkgs.python311Packages.ffmpeg-python
    # pkgs.python311Packages.openai-whisper
    # pkgs.python311Packages.gunicorn
    # pkgs.python311Packages.APScheduler
    # pkgs.python311Packages.srt
    # pkgs.python311Packages.numpy
    # pkgs.python311Packages.torch
    # pkgs.python311Packages.google-auth
    # pkgs.python311Packages.google-auth-oauthlib
    # pkgs.python311Packages.google-auth-httplib2
    # pkgs.python311Packages.google-api-python-client
    # pkgs.python311Packages.google-cloud-storage
    # pkgs.python311Packages.psutil
    # pkgs.python311Packages.boto3
    
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        # npm-install = "npm install";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
      };
    };
  };
}

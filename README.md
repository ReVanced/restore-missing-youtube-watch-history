<p align="center">
  <picture>
    <source
      width="256px"
      media="(prefers-color-scheme: dark)"
      srcset="assets/revanced-headline/revanced-headline-vertical-dark.svg"
    >
    <img 
      width="256px"
      src="assets/revanced-headline/revanced-headline-vertical-light.svg"
    >
  </picture>
  <br>
  <a href="https://revanced.app/">
     <picture>
         <source height="24px" media="(prefers-color-scheme: dark)" srcset="assets/revanced-logo/revanced-logo-round.svg" />
         <img height="24px" src="assets/revanced-logo/revanced-logo-round.svg" />
     </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="https://github.com/ReVanced">
       <picture>
           <source height="24px" media="(prefers-color-scheme: dark)" srcset="https://i.ibb.co/dMMmCrW/Git-Hub-Mark.png" />
           <img height="24px" src="https://i.ibb.co/9wV3HGF/Git-Hub-Mark-Light.png" />
       </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="http://revanced.app/discord">
       <picture>
           <source height="24px" media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/13122796/178032563-d4e084b7-244e-4358-af50-26bde6dd4996.png" />
           <img height="24px" src="https://user-images.githubusercontent.com/13122796/178032563-d4e084b7-244e-4358-af50-26bde6dd4996.png" />
       </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="https://reddit.com/r/revancedapp">
       <picture>
           <source height="24px" media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/13122796/178032351-9d9d5619-8ef7-470a-9eec-2744ece54553.png" />
           <img height="24px" src="https://user-images.githubusercontent.com/13122796/178032351-9d9d5619-8ef7-470a-9eec-2744ece54553.png" />
       </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="https://t.me/app_revanced">
      <picture>
         <source height="24px" media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/13122796/178032213-faf25ab8-0bc3-4a94-a730-b524c96df124.png" />
         <img height="24px" src="https://user-images.githubusercontent.com/13122796/178032213-faf25ab8-0bc3-4a94-a730-b524c96df124.png" />
      </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="https://x.com/revancedapp">
      <picture>
         <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/93124920/270180600-7c1b38bf-889b-4d68-bd5e-b9d86f91421a.png">
         <img height="24px" src="https://user-images.githubusercontent.com/93124920/270108715-d80743fa-b330-4809-b1e6-79fbdc60d09c.png" />
      </picture>
   </a>&nbsp;&nbsp;&nbsp;
   <a href="https://www.youtube.com/@ReVanced">
      <picture>
         <source height="24px" media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/13122796/178032714-c51c7492-0666-44ac-99c2-f003a695ab50.png" />
         <img height="24px" src="https://user-images.githubusercontent.com/13122796/178032714-c51c7492-0666-44ac-99c2-f003a695ab50.png" />
     </picture>
   </a>
   <br>
   <br>
   Continuing the legacy of Vanced
</p>

# ⌛ Restore missing YouTube watch history

Script to import missing YouTube watch history

## ❓ About

This script is used to restore the missing YouTube watch history if you used the ReVanced `Client spoof` patch for YouTube.  
Please remember that it is not meant to be a general-purpose tool for recording watch history. It has specialized functionality for ReVanced to recover from the incident when watch history has disappeared. 

## ⚠️ Disclaimer

> [!WARNING]
> If you need help, you can visit our links at [revanced.app](https://revanced.app) or join our [Discord](https://revanced.app/discord).
> # Do **NOT** use the ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/c3717a3f-6751-4f87-8318-3c5f0f3e4075) channel. Instead use the ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/d3ad95cb-8575-4a28-912b-8bfa64939e58) channel

> [!WARNING]
> This script automates your YouTube account, which is not in terms of YouTube's service. Use this script with caution.

## ✅ Usage

To learn how to use the script and restore your history, follow the steps for your OS:

<details>
  <summary>Windows</summary>
  
1. Install the latest Python from [Microsoft Store](https://apps.microsoft.com/detail/9pjpw5ldxlz5?hl=en-US&gl=US) or [python.org](https://www.python.org/downloads/).
1. Download the project and extract the ZIP somewhere

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/951762e7-cf85-4463-8eec-2a2dc29dfdbd)

1. Open CMD in the directory where `main.py` is located

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/bfaf6f2d-d202-49d5-9618-dea217d11056)

1. install the required packages.

   ```bash
   pip install -r requirements.txt
   ```

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/2800303f-a615-40b5-8b77-e9ad12e884dd)

1. Go to [Google Takeout](https://takeout.google.com/settings/takeout).
1. Only tick "YouTube and YouTube Music"

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/a8716a51-7898-4b74-813f-9de2ac4ba869)
   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/a0d9768c-c61e-4881-b15e-7b773a105b7b)

1. Change "Multiple formats" to "JSON" (only for "history")
  
   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/81533fd7-29d1-47d1-b77b-7830d9ab4d41)
   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/e14ccf57-1339-40e9-a48f-3ce6aadf957a)

1. Untick everything in "All YouTube data included" except "history"

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/917812d0-604a-4742-9e20-2961880cfa3d)

1. Click "Next step"

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/b262087a-b688-4030-b68f-3d94b7770fc2)

1. Leave everything as is and click "Create export"

   ![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/3dc1e728-e92f-48f6-90b2-965d0415c968)

After that, you will receive an email with a link to download your history. Download it. You will find a file called `watch-history.json` in the downloaded zip file inside "YouTube and YouTube Music/history".
Place `watch-history.json` in the same directory as `main.py`.

![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/df826e92-9968-4dd7-82fc-485c8841b6ad)

Make sure you are logged into YouTube in your browser. By default, the script will use Chrome. If you use a different browser, use the `--help` option when you run `main.py` to select your browser.

![image](https://github.com/ReVanced/restore-missing-youtube-watch-history/assets/13122796/963f5282-e1a4-4883-94b4-9123462b8526)

Run the script:

> ⚠️ Warning  
> Make sure your browser does not run. Neither in the foreground nor in the background (See Task Manager),
> otherwise, you may get a permission error when running the script.

```bash
python main.py
```

> ℹ️ Note  
> You can use the `--help` option to see all available options.

</details>

Credits to @guillaumematheron for [the original script](https://gist.github.com/guillaumematheron/89f52ffd274ff3ac99f6dc0249bcc331).

## 📜 License

"Restore missing YouTube watch history" is licensed under the GPLv3 license. Please see the [license file](LICENSE) for more information.
[tl;dr](https://www.tldrlegal.com/license/gnu-general-public-license-v3-gpl-3) you may copy, distribute and modify "Restore missing YouTube watch history" as long as you track changes/dates in source files.
Any modifications to "Restore missing YouTube watch history" must also be made available under the GPL, along with build & install instructions.

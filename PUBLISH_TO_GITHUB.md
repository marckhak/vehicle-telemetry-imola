# Publish to GitHub

The repository is already initialized locally on branch `main` and contains the initial commit.

## 1. Create the GitHub repository

Create a new **public** repository named:

`vehicle-telemetry-imola`

Do not initialize it with another README, `.gitignore` or license: they are already included here.

## 2. Add the remote

Replace `YOUR_GITHUB_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/vehicle-telemetry-imola.git
```

## 3. Push

```bash
git push -u origin main
```

## 4. Recommended GitHub settings

- Visibility: **Public**
- Description: `Automotive telemetry and vehicle dynamics analysis application focused on the Imola Circuit.`
- Topics: `python`, `vehicle-dynamics`, `telemetry`, `automotive`, `motorsport`, `imola`, `numpy`, `pandas`, `matplotlib`, `pyside6`
- Enable Issues if you want to track future development.
- The included GitHub Actions workflow will run the unit tests on pushes and pull requests.

## 5. README links

After creating the repository, replace `YOUR_GITHUB_USERNAME` in `README.md` with the real GitHub username so the badge and clone command point to the correct repository.

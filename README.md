# AIDungeon_discord
AI Dungeon 2 for discord. 


Requirements:
- Create new bot application from [here](https://discord.com/developers/applications)
- config.json with Bot token as 'TOKEN'
- Setup [AIDungeon2](https://github.com/AIDungeon/AIDungeon) in 'AIDungeon' directory
- Download the model torrent from [here](https://github-production-repository-file-5c1aeb.s3.amazonaws.com/179196443/3935881?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20200524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200524T230155Z&X-Amz-Expires=300&X-Amz-Signature=822c5bfe9c8a26a2907022ec9f9c1d70f34e285c70a6093e754739aabcab743f&X-Amz-SignedHeaders=host&actor_id=12412913&repo_id=179196443&response-content-disposition=attachment%3Bfilename%3Dmodel_v5.torrent.zip&response-content-type=application%2Fzip)
- Move model directory to AIDungeon/generator/models/
- Run `./AIDungeon/install.sh` to make virtual environment and install dependencies

Run Discord Bot:
- python bot.py
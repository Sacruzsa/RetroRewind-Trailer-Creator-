from __future__ import annotations

import ctypes
import base64
import hashlib
import json
import math
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    import win32com.client  # type: ignore[import-not-found]
except ImportError:
    win32com = None

APP_NAME = "RetroRewind Trailer Creator"
APP_VERSION = "14.0.1"
GAME_PUBLIC = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\RetroRewind\RetroRewind\Content\Movies\VHS\Public"
)
VIDEO_EXTENSIONS = ("*.mp4", "*.mkv", "*.webm", "*.mov", "*.avi", "*.m4v", "*.ts")

LANGUAGES = {"Nederlands": "nl", "English": "en", "Français": "fr", "Deutsch": "de"}

THEME_LABELS = {
    "nl": {
        "classic_vcr": "1. Classic VCR",
        "neon_video_club": "2. Neon Video Club",
        "arcade_recorder": "3. Arcade Recorder",
        "home_computer_1984": "4. Home Computer 1984",
        "scifi_control_deck": "5. Sci-Fi Control Deck",
        "detective_night": "6. Detective Night",
        "light_studio": "7. Light Studio",
        "dark_studio": "8. Dark Studio",
    },
    "en": {
        "classic_vcr": "1. Classic VCR",
        "neon_video_club": "2. Neon Video Club",
        "arcade_recorder": "3. Arcade Recorder",
        "home_computer_1984": "4. Home Computer 1984",
        "scifi_control_deck": "5. Sci-Fi Control Deck",
        "detective_night": "6. Detective Night",
        "light_studio": "7. Light Studio",
        "dark_studio": "8. Dark Studio",
    },
    "fr": {
        "classic_vcr": "1. Magnétoscope classique",
        "neon_video_club": "2. Vidéoclub néon",
        "arcade_recorder": "3. Enregistreur arcade",
        "home_computer_1984": "4. Ordinateur familial 1984",
        "scifi_control_deck": "5. Console de contrôle SF",
        "detective_night": "6. Nuit détective",
        "light_studio": "7. Studio clair",
        "dark_studio": "8. Studio sombre",
    },
    "de": {
        "classic_vcr": "1. Klassischer Videorekorder",
        "neon_video_club": "2. Neon-Videothek",
        "arcade_recorder": "3. Arcade-Rekorder",
        "home_computer_1984": "4. Heimcomputer 1984",
        "scifi_control_deck": "5. Sci-Fi-Kontrollpult",
        "detective_night": "6. Detektivnacht",
        "light_studio": "7. Helles Studio",
        "dark_studio": "8. Dunkles Studio",
    },
}

THEME_DESCRIPTIONS = {
    "nl": {
        "classic_vcr": "Klassieke zwarte videorecorder met zilveren toetsen, groene VFD-display en rode REC-knop.",
        "neon_video_club": "Donkerpaarse videotheekstijl met cyaan en neonroze verlichting en een helderblauw display.",
        "arcade_recorder": "Zwarte arcade-VCR met pixelaccenten, kleurcodes en een groen-amber digitaal display.",
        "home_computer_1984": "Beige thuiscomputer en videorecorder uit 1984 met bruine toetsen en groene CRT-tekst.",
        "scifi_control_deck": "Technisch jaren-tachtig bedieningspaneel met donkerblauw metaal, cyaan lijnen en amber display.",
        "detective_night": "Nachtelijke misdaadseriestijl met petroleumblauw, amber statuslicht en subtiele VHS-sfeer.",
        "light_studio": "Eenvoudig, helder studiothema met witte panelen, zilveren VCR-knoppen en maximale leesbaarheid.",
        "dark_studio": "Rustig donker studiothema met antraciet, witte tekst, blauwe accenten en rode REC-knop.",
    },
    "en": {
        "classic_vcr": "Classic black video recorder with silver keys, green VFD display and a red REC button.",
        "neon_video_club": "Dark purple video-store styling with cyan and neon-pink lighting and a bright blue display.",
        "arcade_recorder": "Black arcade VCR with pixel accents, colour coding and a green-amber digital display.",
        "home_computer_1984": "Beige 1984 home-computer recorder with brown keys and green CRT text.",
        "scifi_control_deck": "Technical eighties control panel with dark blue metal, cyan lines and an amber display.",
        "detective_night": "Night-time detective styling with deep teal, amber status lighting and subtle VHS atmosphere.",
        "light_studio": "Simple bright studio theme with white panels, silver VCR controls and maximum readability.",
        "dark_studio": "Calm dark studio theme with charcoal panels, white text, blue accents and a red REC button.",
    },
    "fr": {
        "classic_vcr": "Magnétoscope noir classique, touches argentées, affichage VFD vert et bouton REC rouge.",
        "neon_video_club": "Vidéoclub violet sombre avec éclairage cyan et rose néon et affichage bleu.",
        "arcade_recorder": "Magnétoscope arcade noir avec accents pixelisés et affichage vert-ambre.",
        "home_computer_1984": "Ordinateur-magnétoscope beige de 1984 avec touches brunes et texte CRT vert.",
        "scifi_control_deck": "Console technique des années 80, métal bleu sombre, lignes cyan et affichage ambre.",
        "detective_night": "Ambiance de série policière nocturne, bleu pétrole et indicateurs ambre.",
        "light_studio": "Thème studio clair, panneaux blancs et commandes VCR argentées très lisibles.",
        "dark_studio": "Thème studio sombre et calme, anthracite, texte blanc et accents bleus.",
    },
    "de": {
        "classic_vcr": "Klassischer schwarzer Videorekorder mit silbernen Tasten, grünem VFD und roter REC-Taste.",
        "neon_video_club": "Dunkelviolette Videothek mit Cyan, Neonpink und hellblauem Display.",
        "arcade_recorder": "Schwarzer Arcade-Videorekorder mit Pixelakzenten und grün-gelbem Display.",
        "home_computer_1984": "Beiger Heimcomputer-Rekorder von 1984 mit braunen Tasten und grünem CRT-Text.",
        "scifi_control_deck": "Technisches Achtziger-Kontrollpult mit dunkelblauem Metall, Cyanlinien und Amberdisplay.",
        "detective_night": "Nächtlicher Krimiserien-Look mit Petrolblau, Amberanzeigen und VHS-Atmosphäre.",
        "light_studio": "Helles, schlichtes Studiothema mit weißen Flächen und silbernen VCR-Tasten.",
        "dark_studio": "Ruhiges dunkles Studiothema mit Anthrazit, weißer Schrift und blauen Akzenten.",
    },
}
TRANSLATIONS = {
    "nl": {
        "subtitle": "Download, converteer en voeg trailers samen voor Retro Rewind.",
        "tab_download": "1. Download", "tab_convert": "2. Converteren", "tab_final": "3. Game Video", "tab_language": "Taal", "theme": "Thema:", "theme_light": "Licht", "theme_dark": "Donker", "theme_mixed": "Licht/donker mix",
        "language_title": "Taal selecteren", "language_help": "Kies de taal voor alle menu's, knoppen en meldingen.", "language": "Taal:",
        "shortcut": "Snelkoppeling", "instructions": "Gebruiksaanwijzing",
        "video_links": "Videolinks", "video_links_help": "Plaats één link per regel. Elke geslaagde link wordt automatisch uit het tekstvak verwijderd.", "links_example": "Voorbeeld: regel 1 = eerste YouTube-link, regel 2 = tweede YouTube-link, enzovoort.", "paste": "Plakken", "cut": "Knippen", "copy": "Kopiëren", "select_all": "Alles selecteren",
        "download": "Download", "open_downloads": "Open downloads", "clear_all": "Alles wissen",
        "convert_title": "Video's converteren", "convert_help": "Uitvoer: MP4, 512×512, H.264, AAC stereo 48 kHz en constante 30 fps.",
        "choose_videos": "Video's kiezen", "convert": "Converteren", "clear_list": "Lijst wissen", "open_converted": "Open converted videos", "folder_converted": "Map geconverteerde video's", "refresh_game_videos": "Vernieuwen", "refresh_convert_videos": "Vernieuwen", "convert_source_videos": "Video's klaar om te converteren", "converted_videos_title": "Reeds geconverteerde video's",
        "final_title": "Game Video samenstellen", "final_help": "Zet de clips in de juiste volgorde. Alle clips worden opnieuw genormaliseerd om audio en video synchroon te houden.",
        "add_clips": "Clips toevoegen", "up": "Omhoog", "down": "Omlaag", "remove": "Uit lijst verwijderen", "delete_file": "Bestand verwijderen", "preview": "Video’s", "preview_title": "Video’s", "preview_missing": "Er is nog geen gemaakte video gevonden.", "play_video": "Video afspelen", "manual": "HANDLEIDING", "stop": "STOP",
        "delete_confirm": "Wil je de geselecteerde video definitief verwijderen?\n\n{path}\n\nHet bestand wordt ook uit de gekoppelde map verwijderd.", "delete_confirm_many": "Wil je deze {count} geselecteerde video’s definitief verwijderen?\n\nDe bestanden worden ook uit de gekoppelde map verwijderd.", "delete_done": "{count} videobestand(en) verwijderd.", "delete_failed": "Het bestand kon niet worden verwijderd:\n{path}\n\n{error}",
        "save_as": "Opslaan als:", "browse": "Browse", "create_final": "Genereer Game Video", "record_game_video": "REC", "sequence_preview": "Volgorde bekijken", "open_final": "Game Video Locatie", "created_game_videos": "Gecreëerde Game Video’s", "downloaded_videos": "Gedownloade video’s", "converted_preview_videos": "Geconverteerde video’s",
        "view": "Weergave", "list_view": "Lijst", "icon_view": "Pictogrammen",
        "item_count": "Aantal video's: {count}",
        "progress": "Voortgang", "clear_log": "Log wissen", "ready": "Gereed", "minimize": "Minimaliseren", "show": "Tonen",
        "shortcut_title": "Snelkoppeling maken", "shortcut_help": "Het bureaublad is standaard geselecteerd. Kies desgewenst een andere locatie.",
        "other_location": "Andere locatie", "create_shortcut": "Snelkoppeling maken", "cancel": "Annuleren",
        "instructions_text": 'VOLLEDIGE HANDLEIDING — RETROREWIND TRAILER CREATOR\n\n1. VCR-NAVIGATIE\n⏮ DOWNLOAD opent de downloadfunctie. ◀◀ CONVERT opent de conversiefunctie. ▶ GAME VIDEO opent de samensteller. ▣ VIDEO’S toont geconverteerde video’s en gemaakte Game Video’s. ⏏ INSTELLINGEN opent taal, thema, mappen, snelkoppeling en contact. 📖 HANDLEIDING opent deze uitleg.\n\n2. DOWNLOAD\nPlak één volledige YouTube-link per regel. Gebruik Plakken, Knippen, Kopiëren, Alles selecteren en Alles wissen om de lijst te beheren. Download start de verwerking. Open downloads opent de ingestelde downloadmap. Geslaagde links verdwijnen automatisch; mislukte links blijven staan.\n\n3. CONVERT\nDe eerste tab toont video’s die klaarstaan om geconverteerd te worden. Converteren maakt MP4-video’s van 512×512 met H.264, AAC stereo 48 kHz en 30 fps. Vernieuwen leest beide mappen opnieuw in. Lijst wissen leegt alleen de bronlijst. De tweede tab toont de reeds geconverteerde video’s. De knop Map geconverteerde video’s boven de lijst en Open converted videos onder de lijst openen dezelfde ingestelde uitvoermap. Lijst- en pictogramweergave zijn beschikbaar.\n\n4. GAME VIDEO\nVernieuwen laadt alle geconverteerde clips opnieuw. ▲ en ▼ wijzigen de volgorde en 🗑 verwijdert geselecteerde clips na bevestiging. ▶ maakt en opent een tijdelijke preview van de volledige clipvolgorde. De rode REC-knop genereert de definitieve Game Video. Game Video Locatie opent de ingestelde opslagmap en de Steam-map. Opslaan als en Browse bepalen het doelbestand.\n\n5. PREVIEW\nDe algemene VIDEO’S-knop opent een pop-up met twee afzonderlijke rubrieken: geconverteerde video’s en gegenereerde Game Video’s. Play, Pause en Stop bedienen de speler. Gebruik −10s en +10s om te spoelen, de tijdlijn om naar een positie te springen en de volumeregelaar voor het geluidsniveau. Beeld en audio worden bij zoeken samen opnieuw gestart.\n\n6. INSTELLINGEN\nWeergave bevat thema en opslagmappen. Taal verandert alle teksten. Snelkoppeling maakt een Windows-snelkoppeling. Contact toont ondersteuningsinformatie. Een taal- of themawijziging voert een snelle volledige herstart uit zodat alle functies correct worden herladen.\n\n7. VOORTGANG EN MELDINGEN\nTijdens downloaden, converteren en genereren verschijnt een VCR-popup met status, digitaal audiospectrum en log. Sluit de applicatie niet tijdens een actieve verwerking.\n\n8. VEILIG GEBRUIK\nGebruik alleen video’s waarvoor je toestemming hebt. Controleer altijd de geconverteerde clips en de uiteindelijke Game Video voordat je bronbestanden verwijdert.',
        "select_videos": "Kies video's", "video_files": "Videobestanden", "all_files": "Alle bestanden",
        "select_clips": "Kies clips in de gewenste volgorde", "mp4_files": "MP4-bestanden", "all_video_files": "Alle videobestanden",
        "save_final": "Eindvideo opslaan", "mp4_video": "MP4-video", "choose_shortcut": "Kies locatie voor de snelkoppeling",
        "need_url": "Geef minstens één videolink in.", "busy": "Er is al een bewerking bezig.",
        "shortcut_done": "Snelkoppeling gemaakt:\n{path}", "close_busy": "Er is nog een bewerking bezig. Toch afsluiten?",
        "missing_file": "Bestand niet gevonden:\n{path}", "missing_clip": "Clip niet gevonden:\n{path}",
        "download_done": "Downloadopdracht voltooid.\n\nNieuwe bestanden: {count}", "convert_done": "{count} video('s) succesvol geconverteerd.",
        "final_done": "Eindvideo succesvol gemaakt:\n{path}", "ffmpeg_missing": "FFmpeg werd niet gevonden:\n{path}\n\nBouw de applicatie opnieuw met RetroRewind Trailer Creator Setup.exe.",
        "yt_missing": "yt-dlp ontbreekt. Bouw de applicatie opnieuw met het buildscript.",
    },
    "en": {
        "subtitle": "Download, convert and combine trailers for Retro Rewind.",
        "tab_download": "1. Download", "tab_convert": "2. Convert", "tab_final": "3. Game Video", "tab_language": "Language", "theme": "Theme:", "theme_light": "Light", "theme_dark": "Dark", "theme_mixed": "Light/dark mix",
        "language_title": "Select language", "language_help": "Choose the language for all menus, buttons and messages.", "language": "Language:",
        "shortcut": "Shortcut", "instructions": "User guide",
        "video_links": "Video links", "video_links_help": "Enter one link per line. Every successful link is automatically removed from the text box.", "links_example": "Example: line 1 = first YouTube link, line 2 = second YouTube link, and so on.", "paste": "Paste", "cut": "Cut", "copy": "Copy", "select_all": "Select all",
        "download": "Download", "open_downloads": "Open downloads", "clear_all": "Clear all",
        "convert_title": "Convert videos", "convert_help": "Output: MP4, 512×512, H.264, AAC stereo 48 kHz and constant 30 fps.",
        "choose_videos": "Choose videos", "convert": "Convert", "clear_list": "Clear list", "open_converted": "Open converted videos", "folder_converted": "Converted videos folder", "refresh_game_videos": "Refresh", "refresh_convert_videos": "Refresh", "convert_source_videos": "Videos ready to convert", "converted_videos_title": "Converted videos",
        "final_title": "Create Game Video", "final_help": "Put the clips in the correct order. All clips are normalized again to keep audio and video synchronized.",
        "add_clips": "Add clips", "up": "Up", "down": "Down", "remove": "Remove from list", "delete_file": "Delete file", "preview": "Videos", "preview_title": "Videos", "preview_missing": "No created video was found yet.", "play_video": "Play video", "manual": "MANUAL", "stop": "STOP",
        "delete_confirm": "Permanently delete the selected video?\n\n{path}\n\nThe file will also be removed from the linked folder.", "delete_confirm_many": "Permanently delete these {count} selected videos?\n\nThe files will also be removed from the linked folder.", "delete_done": "Deleted {count} video file(s).", "delete_failed": "The file could not be deleted:\n{path}\n\n{error}",
        "save_as": "Save as:", "browse": "Browse", "create_final": "Generate Game Video", "record_game_video": "REC", "sequence_preview": "Preview sequence", "open_final": "Game Video Location", "created_game_videos": "Created Game Videos", "downloaded_videos": "Downloaded videos", "converted_preview_videos": "Converted videos",
        "view": "View", "list_view": "List", "icon_view": "Icons",
        "item_count": "Videos: {count}",
        "progress": "Progress", "clear_log": "Clear log", "ready": "Ready", "minimize": "Minimize", "show": "Show",
        "shortcut_title": "Create shortcut", "shortcut_help": "The desktop is selected by default. Choose another location if needed.",
        "other_location": "Other location", "create_shortcut": "Create shortcut", "cancel": "Cancel",
        "instructions_text": 'COMPLETE USER GUIDE — RETROREWIND TRAILER CREATOR\n\n1. VCR NAVIGATION\n⏮ DOWNLOAD opens downloads. ◀◀ CONVERT opens conversion. ▶ GAME VIDEO opens the builder. ▣ VIDEO’S lists converted videos and created Game Videos. ⏏ SETTINGS opens language, theme, folders, shortcut and contact. 📖 MANUAL opens this guide.\n\n2. DOWNLOAD\nPaste one complete YouTube URL per line. Paste, Cut, Copy, Select all and Clear all manage the list. Download starts processing. Open downloads opens the configured folder. Successful links are removed automatically; failed links remain.\n\n3. CONVERT\nThe first tab lists videos ready to convert. Convert creates 512×512 MP4 files using H.264, AAC stereo 48 kHz and 30 fps. Refresh reloads both folders. Clear list only clears the source list. The second tab lists converted videos. Converted videos folder above the list and Open converted videos below it open the configured output folder. List and icon views are available.\n\n4. GAME VIDEO\nRefresh reloads converted clips. ▲ and ▼ change their order and 🗑 deletes selected clips after confirmation. ▶ creates and opens a temporary preview of the complete sequence. The red REC button generates the final Game Video. Game Video Location opens the configured output folder and the Steam folder. Save as and Browse set the destination file.\n\n5. PREVIEW\nThe main VIDEOS button opens a popup with two separate sections: converted videos and generated Game Videos. Play, Pause and Stop control playback. Use −10s and +10s to seek, the timeline to jump to a position, and the volume slider to change sound level. Audio and video restart together after seeking.\n\n6. SETTINGS\nDisplay contains theme and storage folders. Language changes all text. Shortcut creates a Windows shortcut. Contact shows support information. Language or theme changes perform a quick full restart so every feature reloads correctly.\n\n7. PROGRESS\nDownloading, converting and generating show a VCR popup with status, digital audio spectrum and log. Do not close the application during an active operation.\n\n8. LEGAL USE\nOnly use videos you are allowed to use. Always verify converted clips and the final Game Video before deleting source files.',
        "select_videos": "Choose videos", "video_files": "Video files", "all_files": "All files",
        "select_clips": "Choose clips in the desired order", "mp4_files": "MP4 files", "all_video_files": "All video files",
        "save_final": "Save final video", "mp4_video": "MP4 video", "choose_shortcut": "Choose shortcut location",
        "need_url": "Enter at least one video link.", "busy": "Another operation is already running.",
        "shortcut_done": "Shortcut created:\n{path}", "close_busy": "An operation is still running. Exit anyway?",
        "missing_file": "File not found:\n{path}", "missing_clip": "Clip not found:\n{path}",
        "download_done": "Download task completed.\n\nNew files: {count}", "convert_done": "{count} video(s) converted successfully.",
        "final_done": "Final video created successfully:\n{path}", "ffmpeg_missing": "FFmpeg was not found:\n{path}\n\nBuild the application again with RetroRewind Trailer Creator Setup.exe.",
        "yt_missing": "yt-dlp is missing. Build the application again with the build script.",
    },
    "fr": {
        "subtitle": "Téléchargez, convertissez et assemblez des bandes-annonces pour Retro Rewind.",
        "tab_download": "1. Télécharger", "tab_convert": "2. Convertir", "tab_final": "3. Game Video", "tab_language": "Langue", "theme": "Thème :", "theme_light": "Clair", "theme_dark": "Sombre", "theme_mixed": "Mix clair/sombre",
        "language_title": "Sélection de la langue", "language_help": "Choisissez la langue de tous les menus, boutons et messages.", "language": "Langue :",
        "shortcut": "Raccourci", "instructions": "Mode d'emploi",
        "video_links": "Liens vidéo", "video_links_help": "Saisissez un lien par ligne. Chaque lien réussi est automatiquement supprimé de la zone de texte.", "links_example": "Exemple : ligne 1 = premier lien YouTube, ligne 2 = deuxième lien, etc.", "paste": "Coller", "cut": "Couper", "copy": "Copier", "select_all": "Tout sélectionner",
        "download": "Télécharger", "open_downloads": "Ouvrir les téléchargements", "clear_all": "Tout effacer",
        "convert_title": "Convertir des vidéos", "convert_help": "Sortie : MP4, 512×512, H.264, AAC stéréo 48 kHz et 30 fps constants.",
        "choose_videos": "Choisir des vidéos", "convert": "Convertir", "clear_list": "Effacer la liste", "open_converted": "Ouvrir les vidéos converties", "folder_converted": "Dossier des vidéos converties", "refresh_game_videos": "Actualiser", "refresh_convert_videos": "Actualiser", "convert_source_videos": "Vidéos à convertir", "converted_videos_title": "Vidéos déjà converties",
        "final_title": "Créer la Game Video", "final_help": "Placez les clips dans le bon ordre. Tous les clips sont à nouveau normalisés pour synchroniser l'audio et la vidéo.",
        "add_clips": "Ajouter des clips", "up": "Monter", "down": "Descendre", "remove": "Retirer de la liste", "delete_file": "Supprimer le fichier", "preview": "Vidéos", "preview_title": "Vidéos", "preview_missing": "Aucune vidéo créée n’a encore été trouvée.", "play_video": "Lire la vidéo", "manual": "MANUEL", "stop": "STOP",
        "delete_confirm": "Supprimer définitivement la vidéo sélectionnée ?\n\n{path}\n\nLe fichier sera également supprimé du dossier lié.", "delete_confirm_many": "Supprimer définitivement les {count} vidéos sélectionnées ?\n\nLes fichiers seront également supprimés du dossier lié.", "delete_done": "{count} fichier(s) vidéo supprimé(s).", "delete_failed": "Impossible de supprimer le fichier :\n{path}\n\n{error}",
        "save_as": "Enregistrer sous :", "browse": "Parcourir", "create_final": "Générer la Game Video", "record_game_video": "REC", "sequence_preview": "Aperçu de l’ordre", "open_final": "Emplacement Game Video", "created_game_videos": "Game Videos créées", "downloaded_videos": "Vidéos téléchargées", "converted_preview_videos": "Vidéos converties",
        "view": "Affichage", "list_view": "Liste", "icon_view": "Icônes",
        "item_count": "Vidéos : {count}",
        "progress": "Progression", "clear_log": "Effacer le journal", "ready": "Prêt", "minimize": "Réduire", "show": "Afficher",
        "shortcut_title": "Créer un raccourci", "shortcut_help": "Le bureau est sélectionné par défaut. Choisissez un autre emplacement si nécessaire.",
        "other_location": "Autre emplacement", "create_shortcut": "Créer le raccourci", "cancel": "Annuler",
        "instructions_text": 'GUIDE COMPLET — RETROREWIND TRAILER CREATOR\n\n1. NAVIGATION VCR\n⏮ TÉLÉCHARGER ouvre le téléchargement. ◀◀ CONVERTIR ouvre la conversion. ▶ GAME VIDEO ouvre l’assemblage. ▣ VIDÉOS affiche les vidéos converties et les Game Videos créées. ⏏ PARAMÈTRES ouvre langue, thème, dossiers, raccourci et contact. 📖 MANUEL ouvre ce guide.\n\n2. TÉLÉCHARGEMENT\nCollez une URL YouTube complète par ligne. Les commandes Coller, Couper, Copier, Tout sélectionner et Tout effacer gèrent la liste. Télécharger lance le traitement. Ouvrir downloads ouvre le dossier configuré.\n\n3. CONVERSION\nLe premier onglet affiche les vidéos à convertir. Convertir crée des MP4 512×512 en H.264, AAC stéréo 48 kHz et 30 fps. Actualiser recharge les deux dossiers. Effacer la liste vide uniquement la liste source. Le deuxième onglet affiche les vidéos converties. Dossier des vidéos converties au-dessus et Ouvrir les vidéos converties en dessous ouvrent le dossier de sortie.\n\n4. GAME VIDEO\nActualiser recharge les clips. Générer la Game Video assemble les clips dans l’ordre affiché. Emplacement Game Video ouvre le dossier final. ▲ et ▼ changent l’ordre. 🗑 supprime définitivement les fichiers sélectionnés après confirmation. ▶ lit le clip sélectionné. Enregistrer sous et Parcourir définissent la sortie.\n\n5. APERÇU\nChoisissez une vidéo convertie ou une Game Video. Play, Pause et Stop contrôlent la lecture. −10s, +10s, la ligne de temps et le volume permettent de naviguer et régler le son. Audio et vidéo redémarrent ensemble après un déplacement.\n\n6. PARAMÈTRES ET PROGRESSION\nLes paramètres gèrent thème, langue, dossiers, raccourci et contact. Un changement de langue ou de thème redémarre rapidement l’interface. Les opérations affichent une fenêtre VCR avec état, spectre audio numérique et journal.\n\nUTILISATION LÉGALE\nUtilisez uniquement des vidéos pour lesquelles vous avez une autorisation.',
        "select_videos": "Choisir des vidéos", "video_files": "Fichiers vidéo", "all_files": "Tous les fichiers",
        "select_clips": "Choisir les clips dans l'ordre souhaité", "mp4_files": "Fichiers MP4", "all_video_files": "Tous les fichiers vidéo",
        "save_final": "Enregistrer la vidéo finale", "mp4_video": "Vidéo MP4", "choose_shortcut": "Choisir l'emplacement du raccourci",
        "need_url": "Saisissez au moins un lien vidéo.", "busy": "Une autre opération est déjà en cours.",
        "shortcut_done": "Raccourci créé :\n{path}", "close_busy": "Une opération est encore en cours. Quitter quand même ?",
        "missing_file": "Fichier introuvable :\n{path}", "missing_clip": "Clip introuvable :\n{path}",
        "download_done": "Téléchargement terminé.\n\nNouveaux fichiers : {count}", "convert_done": "{count} vidéo(s) convertie(s) avec succès.",
        "final_done": "Vidéo finale créée avec succès :\n{path}", "ffmpeg_missing": "FFmpeg est introuvable :\n{path}\n\nReconstruisez l'application avec RetroRewind Trailer Creator Setup.exe.",
        "yt_missing": "yt-dlp est manquant. Reconstruisez l'application avec le script de compilation.",
    },
    "de": {
        "subtitle": "Trailer für Retro Rewind herunterladen, konvertieren und zusammenfügen.",
        "tab_download": "1. Download", "tab_convert": "2. Konvertieren", "tab_final": "3. Game Video", "tab_language": "Sprache", "theme": "Design:", "theme_light": "Hell", "theme_dark": "Dunkel", "theme_mixed": "Hell-Dunkel-Mix",
        "language_title": "Sprache auswählen", "language_help": "Wählen Sie die Sprache für alle Menüs, Schaltflächen und Meldungen.", "language": "Sprache:",
        "shortcut": "Verknüpfung", "instructions": "Bedienungsanleitung",
        "video_links": "Videolinks", "video_links_help": "Geben Sie einen Link pro Zeile ein. Jeder erfolgreiche Link wird automatisch aus dem Textfeld entfernt.", "links_example": "Beispiel: Zeile 1 = erster YouTube-Link, Zeile 2 = zweiter Link usw.", "paste": "Einfügen", "cut": "Ausschneiden", "copy": "Kopieren", "select_all": "Alles auswählen",
        "download": "Download", "open_downloads": "Downloads öffnen", "clear_all": "Alles löschen",
        "convert_title": "Videos konvertieren", "convert_help": "Ausgabe: MP4, 512×512, H.264, AAC Stereo 48 kHz und konstante 30 fps.",
        "choose_videos": "Videos auswählen", "convert": "Konvertieren", "clear_list": "Liste löschen", "open_converted": "Konvertierte Videos öffnen", "folder_converted": "Ordner konvertierte Videos", "refresh_game_videos": "Aktualisieren", "refresh_convert_videos": "Aktualisieren", "convert_source_videos": "Videos zum Konvertieren", "converted_videos_title": "Bereits konvertierte Videos",
        "final_title": "Game Video erstellen", "final_help": "Bringen Sie die Clips in die richtige Reihenfolge. Alle Clips werden erneut normalisiert, damit Audio und Video synchron bleiben.",
        "add_clips": "Clips hinzufügen", "up": "Nach oben", "down": "Nach unten", "remove": "Aus Liste entfernen", "delete_file": "Datei löschen", "preview": "Videos", "preview_title": "Videos", "preview_missing": "Es wurde noch kein erstelltes Video gefunden.", "play_video": "Video abspielen", "manual": "ANLEITUNG", "stop": "STOP",
        "delete_confirm": "Das ausgewählte Video endgültig löschen?\n\n{path}\n\nDie Datei wird auch aus dem verknüpften Ordner entfernt.", "delete_confirm_many": "Diese {count} ausgewählten Videos endgültig löschen?\n\nDie Dateien werden auch aus dem verknüpften Ordner entfernt.", "delete_done": "{count} Videodatei(en) gelöscht.", "delete_failed": "Die Datei konnte nicht gelöscht werden:\n{path}\n\n{error}",
        "save_as": "Speichern unter:", "browse": "Durchsuchen", "create_final": "Game Video generieren", "record_game_video": "REC", "sequence_preview": "Reihenfolge ansehen", "open_final": "Game-Video-Speicherort", "created_game_videos": "Erstellte Game Videos", "downloaded_videos": "Heruntergeladene Videos", "converted_preview_videos": "Konvertierte Videos",
        "view": "Ansicht", "list_view": "Liste", "icon_view": "Symbole",
        "progress": "Fortschritt", "clear_log": "Protokoll löschen", "ready": "Bereit", "minimize": "Minimieren", "show": "Anzeigen",
        "shortcut_title": "Verknüpfung erstellen", "shortcut_help": "Der Desktop ist standardmäßig ausgewählt. Wählen Sie bei Bedarf einen anderen Speicherort.",
        "other_location": "Anderer Speicherort", "create_shortcut": "Verknüpfung erstellen", "cancel": "Abbrechen",
        "instructions_text": 'VOLLSTÄNDIGE ANLEITUNG — RETROREWIND TRAILER CREATOR\n\n1. VCR-NAVIGATION\n⏮ DOWNLOAD öffnet Downloads. ◀◀ KONVERTIEREN öffnet die Konvertierung. ▶ GAME VIDEO öffnet den Builder. ▣ VIDEOS zeigt konvertierte Videos und erstellte Game Videos. ⏏ EINSTELLUNGEN öffnet Sprache, Design, Ordner, Verknüpfung und Kontakt. 📖 ANLEITUNG öffnet diesen Text.\n\n2. DOWNLOAD\nFügen Sie pro Zeile eine vollständige YouTube-URL ein. Einfügen, Ausschneiden, Kopieren, Alles auswählen und Alles löschen verwalten die Liste. Download startet den Vorgang. Downloads öffnen öffnet den konfigurierten Ordner.\n\n3. KONVERTIEREN\nOben stehen Videos zum Konvertieren. Konvertieren erstellt 512×512-MP4-Dateien mit H.264, AAC Stereo 48 kHz und 30 fps. Aktualisieren lädt beide Ordner neu. Liste löschen leert nur die Quellliste. Unten stehen bereits konvertierte Videos. Ordner konvertierte Videos oberhalb und Konvertierte Videos öffnen unterhalb öffnen den Ausgabeordner.\n\n4. GAME VIDEO\nAktualisieren lädt Clips neu. Game Video generieren verbindet Clips in der angezeigten Reihenfolge. Game-Video-Speicherort öffnet den final-Ordner. ▲ und ▼ ändern die Reihenfolge. 🗑 löscht ausgewählte Dateien nach Bestätigung endgültig. ▶ spielt den ausgewählten Clip. Speichern unter und Durchsuchen bestimmen das Ziel.\n\n5. VORSCHAU\nWählen Sie ein konvertiertes Video oder ein erstelltes Game Video. Play, Pause und Stop steuern die Wiedergabe. −10s, +10s, Zeitleiste und Lautstärkeregler steuern Position und Ton. Audio und Video starten nach dem Suchen gemeinsam neu.\n\n6. EINSTELLUNGEN UND FORTSCHRITT\nEinstellungen verwalten Design, Sprache, Ordner, Verknüpfung und Kontakt. Sprach- oder Designwechsel laden die Oberfläche schnell neu. Vorgänge zeigen ein VCR-Fenster mit Status, digitalem Audiospektrum und Protokoll.\n\nRECHTMÄSSIGE NUTZUNG\nVerwenden Sie nur Videos, die Sie verwenden dürfen.',
        "select_videos": "Videos auswählen", "video_files": "Videodateien", "all_files": "Alle Dateien",
        "select_clips": "Clips in gewünschter Reihenfolge auswählen", "mp4_files": "MP4-Dateien", "all_video_files": "Alle Videodateien",
        "save_final": "Endvideo speichern", "mp4_video": "MP4-Video", "choose_shortcut": "Speicherort der Verknüpfung wählen",
        "need_url": "Geben Sie mindestens einen Videolink ein.", "busy": "Es läuft bereits ein anderer Vorgang.",
        "shortcut_done": "Verknüpfung erstellt:\n{path}", "close_busy": "Es läuft noch ein Vorgang. Trotzdem beenden?",
        "missing_file": "Datei nicht gefunden:\n{path}", "missing_clip": "Clip nicht gefunden:\n{path}",
        "download_done": "Download abgeschlossen.\n\nNeue Dateien: {count}", "convert_done": "{count} Video(s) erfolgreich konvertiert.",
        "final_done": "Endvideo erfolgreich erstellt:\n{path}", "ffmpeg_missing": "FFmpeg wurde nicht gefunden:\n{path}\n\nErstellen Sie die Anwendung erneut mit RetroRewind Trailer Creator Setup.exe.",
        "yt_missing": "yt-dlp fehlt. Erstellen Sie die Anwendung erneut mit dem Build-Skript.",
    },
}


_SETTINGS_TEXT = {
    "nl": {"settings": "Instellingen", "settings_title": "Instellingen", "folders": "Maplocaties", "downloads_folder": "Downloads", "converted_folder": "Geconverteerde video's", "final_folder": "Finale video's", "choose_folder": "Kiezen", "save": "Opslaan", "contact": "Contact", "contact_title": "Contact opnemen", "contact_name": "Naam", "contact_subject": "Onderwerp", "contact_message": "Beschrijving / gewenste aanpassing", "contact_images": "Afbeeldingen of bestanden", "add_files": "Bestanden toevoegen", "remove_selected": "Selectie verwijderen", "send": "Verzenden", "contact_sent": "Het bericht is via Outlook verzonden.", "contact_fallback": "Automatisch verzenden was niet mogelijk. Er wordt een nieuw bericht in uw standaard mailprogramma geopend.", "contact_need_message": "Vul een onderwerp en bericht in.", "folder_saved": "Instellingen opgeslagen.", "folder_error": "De gekozen map kon niet worden aangemaakt:\n{path}", "appearance": "Weergave", "shortcut_section": "Hulpmiddelen", "settings_intro": "Beheer de weergave, opslagmappen en ondersteuning op één duidelijke plaats.", "appearance_help": "Kies de taal en het kleurenschema van de applicatie.", "folders_help": "Bepaal waar bronvideo’s, geconverteerde clips en eindvideo’s worden opgeslagen.", "support_help": "Maak een snelkoppeling of stuur een bericht met eventuele bijlagen.", "tab_appearance": "Weergave", "tab_folders": "Mappen", "tab_support": "Ondersteuning", "tab_language_settings": "Taal", "tab_shortcut_settings": "Snelkoppeling", "tab_contact_settings": "Contact", "language_instant": "Na uw keuze wordt de applicatie automatisch snel opnieuw gestart.", "contact_help": "Stuur een bericht met eventuele afbeeldingen of bestanden.", "theme_preview": "Thema wordt toegepast na Opslaan.", "folder_hint": "Kies een bovenliggende locatie; de vereiste map wordt automatisch aangemaakt.", "open_folder": "Openen"},
    "en": {"settings": "Settings", "settings_title": "Settings", "folders": "Folder locations", "downloads_folder": "Downloads", "converted_folder": "Converted videos", "final_folder": "Final videos", "choose_folder": "Choose", "save": "Save", "contact": "Contact", "contact_title": "Contact", "contact_name": "Name", "contact_subject": "Subject", "contact_message": "Description / requested change", "contact_images": "Images or files", "add_files": "Add files", "remove_selected": "Remove selected", "send": "Send", "contact_sent": "The message was sent through Outlook.", "contact_fallback": "Automatic sending was unavailable. A new message will be opened in your default mail application.", "contact_need_message": "Enter a subject and message.", "folder_saved": "Settings saved.", "folder_error": "The selected folder could not be created:\n{path}", "appearance": "Appearance", "shortcut_section": "Tools", "settings_intro": "Manage appearance, storage folders and support from one clear place.", "appearance_help": "Choose the application language and colour scheme.", "folders_help": "Choose where source videos, converted clips and final videos are stored.", "support_help": "Create a shortcut or send a message with optional attachments.", "tab_appearance": "Appearance", "tab_folders": "Folders", "tab_support": "Support", "tab_language_settings": "Language", "tab_shortcut_settings": "Shortcut", "tab_contact_settings": "Contact", "language_instant": "After your selection, the application restarts automatically.", "contact_help": "Send a message with optional images or files.", "theme_preview": "The theme is applied after Save.", "folder_hint": "Choose a parent location; the required folder is created automatically.", "open_folder": "Open"},
    "fr": {"settings": "Paramètres", "settings_title": "Paramètres", "folders": "Emplacements des dossiers", "downloads_folder": "Téléchargements", "converted_folder": "Vidéos converties", "final_folder": "Vidéos finales", "choose_folder": "Choisir", "save": "Enregistrer", "contact": "Contact", "contact_title": "Contacter", "contact_name": "Nom", "contact_subject": "Objet", "contact_message": "Description / modification souhaitée", "contact_images": "Images ou fichiers", "add_files": "Ajouter des fichiers", "remove_selected": "Retirer la sélection", "send": "Envoyer", "contact_sent": "Le message a été envoyé via Outlook.", "contact_fallback": "L’envoi automatique est indisponible. Un nouveau message va s’ouvrir dans votre application de messagerie.", "contact_need_message": "Saisissez un objet et un message.", "folder_saved": "Paramètres enregistrés.", "folder_error": "Impossible de créer le dossier sélectionné :\n{path}", "appearance": "Affichage", "shortcut_section": "Outils", "settings_intro": "Gérez l’affichage, les dossiers de stockage et l’assistance depuis un écran clair.", "appearance_help": "Choisissez la langue et le thème de couleurs de l’application.", "folders_help": "Choisissez où enregistrer les vidéos sources, converties et finales.", "support_help": "Créez un raccourci ou envoyez un message avec des pièces jointes.", "tab_appearance": "Affichage", "tab_folders": "Dossiers", "tab_support": "Assistance", "tab_language_settings": "Langue", "tab_shortcut_settings": "Raccourci", "tab_contact_settings": "Contact", "language_instant": "Après votre sélection, l’application redémarre automatiquement.", "contact_help": "Envoyez un message avec des images ou fichiers éventuels.", "theme_preview": "Le thème sera appliqué après Enregistrer.", "folder_hint": "Choisissez un emplacement parent ; le dossier requis sera créé automatiquement.", "open_folder": "Ouvrir"},
    "de": {"settings": "Einstellungen", "settings_title": "Einstellungen", "folders": "Ordnerpfade", "downloads_folder": "Downloads", "converted_folder": "Konvertierte Videos", "final_folder": "Finale Videos", "choose_folder": "Auswählen", "save": "Speichern", "contact": "Kontakt", "contact_title": "Kontakt", "contact_name": "Name", "contact_subject": "Betreff", "contact_message": "Beschreibung / gewünschte Anpassung", "contact_images": "Bilder oder Dateien", "add_files": "Dateien hinzufügen", "remove_selected": "Auswahl entfernen", "send": "Senden", "contact_sent": "Die Nachricht wurde über Outlook gesendet.", "contact_fallback": "Automatisches Senden war nicht möglich. Eine neue Nachricht wird im Standard-Mailprogramm geöffnet.", "contact_need_message": "Bitte Betreff und Nachricht eingeben.", "folder_saved": "Einstellungen gespeichert.", "folder_error": "Der ausgewählte Ordner konnte nicht erstellt werden:\n{path}", "appearance": "Darstellung", "shortcut_section": "Werkzeuge", "settings_intro": "Verwalten Sie Darstellung, Speicherordner und Support übersichtlich an einem Ort.", "appearance_help": "Wählen Sie Sprache und Farbschema der Anwendung.", "folders_help": "Legen Sie fest, wo Quellvideos, konvertierte Clips und finale Videos gespeichert werden.", "support_help": "Erstellen Sie eine Verknüpfung oder senden Sie eine Nachricht mit Anhängen.", "tab_appearance": "Darstellung", "tab_folders": "Ordner", "tab_support": "Support", "tab_language_settings": "Sprache", "tab_shortcut_settings": "Verknüpfung", "tab_contact_settings": "Kontakt", "language_instant": "Nach der Auswahl wird die Anwendung automatisch neu gestartet.", "contact_help": "Senden Sie eine Nachricht mit optionalen Bildern oder Dateien.", "theme_preview": "Das Design wird nach Speichern angewendet.", "folder_hint": "Wählen Sie einen übergeordneten Speicherort; der benötigte Ordner wird automatisch erstellt.", "open_folder": "Öffnen"},
}
for _lang, _items in _SETTINGS_TEXT.items():
    TRANSLATIONS.setdefault(_lang, {}).update(_items)


# ---------------------------------------------------------------------------
# Paths and bundled files
# ---------------------------------------------------------------------------
def executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", executable_dir()))
    return base / relative


def local_app_data() -> Path:
    raw = os.environ.get("LOCALAPPDATA")
    return Path(raw) if raw else Path.home() / "AppData" / "Local"


INSTALL_DIR = executable_dir()
DATA_DIR = local_app_data() / APP_NAME

# Media folders are visible and, by default, live next to the installed EXE.
# The installer grants normal users write access to these three folders when
# the program is installed in a protected location such as Program Files.
MEDIA_FOLDER_NAMES = {
    "downloads_dir": f"{APP_NAME} downloads",
    "converted_dir": f"{APP_NAME} converted videos",
    "final_dir": f"{APP_NAME} final",
}
WORKSPACE_DIR = INSTALL_DIR  # Compatibility alias; no .workspace directory is created.
DOWNLOADS_DIR = INSTALL_DIR / MEDIA_FOLDER_NAMES["downloads_dir"]
CONVERTED_DIR = INSTALL_DIR / MEDIA_FOLDER_NAMES["converted_dir"]
FINAL_DIR = INSTALL_DIR / MEDIA_FOLDER_NAMES["final_dir"]
LOGS_DIR = DATA_DIR / "logs"
TEMP_DIR = DATA_DIR / "temp"
FFMPEG = resource_path("tools/ffmpeg.exe" if os.name == "nt" else "tools/ffmpeg")
SETTINGS_FILE = DATA_DIR / "settings.json"

LEGACY_MEDIA_NAMES = {
    "downloads_dir": "downloads",
    "converted_dir": "converted videos",
    "final_dir": "final",
}


def is_legacy_workspace_path(path: Path, key: str) -> bool:
    """Recognise an old .workspace path, even from a previous install location."""
    try:
        return (
            path.name.casefold() == LEGACY_MEDIA_NAMES[key].casefold()
            and path.parent.name.casefold() == ".workspace"
        )
    except (OSError, ValueError):
        return False


def move_directory_contents(old: Path, new: Path) -> None:
    """Move all files without overwriting existing media and remove empty legacy dirs."""
    try:
        if not old.exists() or old.resolve() == new.resolve():
            return
    except OSError:
        return
    new.mkdir(parents=True, exist_ok=True)
    for item in tuple(old.iterdir()):
        target = new / item.name
        if target.exists():
            stem, suffix = target.stem, target.suffix
            counter = 2
            while target.exists():
                target = new / f"{stem} ({counter}){suffix}"
                counter += 1
        try:
            shutil.move(str(item), str(target))
        except OSError:
            continue
    try:
        old.rmdir()
    except OSError:
        pass
    if old.parent.name.casefold() == ".workspace":
        try:
            old.parent.rmdir()
        except OSError:
            pass


# Only application settings/log/temp are created at import time. Media folders
# are resolved from settings first, so an old path can never recreate .workspace.
for directory in (DATA_DIR, LOGS_DIR, TEMP_DIR):
    directory.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def windows_startupinfo() -> subprocess.STARTUPINFO | None:
    if os.name != "nt":
        return None
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startup


def creation_flags() -> int:
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def safe_filename(value: str, max_length: int = 140) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip().rstrip(".")
    return (value[:max_length] or "video").strip()


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for number in range(2, 10000):
        candidate = path.with_name(f"{stem} ({number}){suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Er kon geen unieke bestandsnaam worden gemaakt.")


def desktop_path() -> Path:
    if os.name == "nt":
        buffer = ctypes.create_unicode_buffer(260)
        # CSIDL_DESKTOPDIRECTORY = 0x10
        result = ctypes.windll.shell32.SHGetFolderPathW(None, 0x10, None, 0, buffer)
        if result == 0 and buffer.value:
            return Path(buffer.value)
    return Path.home() / "Desktop"



def hide_support_files() -> None:
    """Keep the application directory clean: only the main EXE stays visible."""
    if os.name != "nt" or not getattr(sys, "frozen", False):
        return
    try:
        root = executable_dir()
        visible_names = {"retrorewind trailer creator.exe"}
        FILE_ATTRIBUTE_HIDDEN = 0x2
        for item in root.iterdir():
            if item.name.lower() in visible_names:
                continue
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(item))
                if attrs != -1:
                    ctypes.windll.kernel32.SetFileAttributesW(str(item), attrs | FILE_ATTRIBUTE_HIDDEN)
            except OSError:
                pass
    except OSError:
        pass

def open_in_explorer(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def open_media_file(path: Path) -> None:
    """Open a media file with the operating system's default player."""
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)
    if os.name == "nt":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def create_windows_shortcut(destination: Path) -> Path:
    """Create a Windows shortcut without launching PowerShell or scripts."""
    if os.name != "nt":
        raise RuntimeError("Snelkoppelingen worden alleen op Windows ondersteund.")

    destination.mkdir(parents=True, exist_ok=True)
    target = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve()
    shortcut = destination / f"{APP_NAME}.lnk"

    if win32com is not None:
        shell = win32com.client.Dispatch("WScript.Shell")
        link = shell.CreateShortcut(str(shortcut))
        link.TargetPath = str(target)
        link.WorkingDirectory = str(INSTALL_DIR)
        link.IconLocation = f"{target},0"
        link.Description = "Download en maak trailers voor Retro Rewind"
        link.Save()
        return shortcut

    # Safe fallback when pywin32 is unavailable: create a standard Windows URL shortcut.
    url_shortcut = destination / f"{APP_NAME}.url"
    file_url = target.as_uri()
    url_shortcut.write_text(
        "[InternetShortcut]\n"
        f"URL={file_url}\n"
        f"IconFile={target}\n"
        "IconIndex=0\n",
        encoding="utf-8",
    )
    return url_shortcut


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict) -> None:
    try:
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    except OSError:
        pass


@dataclass
class ProcessResult:
    returncode: int
    output: str


def run_process(
    command: list[str],
    log: Callable[[str], None],
    cancel_event: threading.Event | None = None,
) -> ProcessResult:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        startupinfo=windows_startupinfo(),
        creationflags=creation_flags(),
    )
    lines: list[str] = []
    assert process.stdout is not None
    while True:
        line = process.stdout.readline()
        if line:
            cleaned = line.rstrip()
            lines.append(cleaned)
            # Keep useful ffmpeg progress and error lines, avoid flooding the UI.
            if any(token in cleaned.lower() for token in ("time=", "error", "invalid", "failed")):
                log(cleaned)
        elif process.poll() is not None:
            break
        if cancel_event and cancel_event.is_set():
            process.terminate()
            raise RuntimeError("De bewerking werd geannuleerd.")
    returncode = process.wait()
    output = "\n".join(lines)
    if returncode != 0:
        tail = "\n".join(lines[-15:])
        raise RuntimeError(f"FFmpeg stopte met foutcode {returncode}.\n\n{tail}")
    return ProcessResult(returncode, output)


def source_has_audio(source: Path) -> bool:
    command = [str(FFMPEG), "-hide_banner", "-i", str(source), "-f", "null", "-"]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        startupinfo=windows_startupinfo(),
        creationflags=creation_flags(),
    )
    return bool(re.search(r"Stream #\S+: Audio:", result.stdout))


def normalized_video_command(source: Path, target: Path) -> list[str]:
    """Create a deterministic CFR clip with timestamps starting at zero.

    Every output uses exactly the same video/audio format. Silent audio is added
    when a source has no audio stream, which makes later concatenation reliable.
    """
    video_filter = (
        "scale=512:512:force_original_aspect_ratio=decrease,"
        "pad=512:512:(ow-iw)/2:(oh-ih)/2,"
        "fps=30,settb=1/30000,setpts=N/(30*TB),setsar=1"
    )
    common_output = [
        "-map", "0:v:0",
        "-vf", video_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-profile:v", "high",
        "-level", "4.0",
        "-r", "30",
        "-fps_mode", "cfr",
        "-video_track_timescale", "30000",
    ]

    if source_has_audio(source):
        audio = [
            "-map", "0:a:0",
            "-af", "aresample=48000:async=1:first_pts=0,asetpts=N/SR/TB",
        ]
        inputs = ["-fflags", "+genpts+discardcorrupt", "-i", str(source)]
    else:
        inputs = [
            "-fflags", "+genpts+discardcorrupt", "-i", str(source),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        ]
        audio = ["-map", "1:a:0", "-shortest"]

    return [
        str(FFMPEG), "-y", "-hide_banner",
        *inputs,
        *common_output,
        *audio,
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-max_muxing_queue_size", "4096",
        "-avoid_negative_ts", "make_zero",
        "-movflags", "+faststart",
        str(target),
    ]


def concat_filter_command(clips: list[Path], target: Path) -> list[str]:
    """Join normalized clips with FFmpeg's concat filter.

    The concat demuxer can preserve timestamp discontinuities from individual
    MP4 files. On longer projects this may result in audio continuing while the
    video stream ends or freezes. Feeding every clip as a separate input and
    resetting both streams to zero before the concat filter avoids that issue.
    There is intentionally no duration limit.
    """
    if not clips:
        raise ValueError("Er zijn geen clips om samen te voegen.")

    command = [str(FFMPEG), "-y", "-hide_banner", "-fflags", "+genpts+discardcorrupt"]
    for clip in clips:
        command.extend(["-i", str(clip)])

    filter_parts: list[str] = []
    concat_inputs: list[str] = []
    for index in range(len(clips)):
        filter_parts.append(
            f"[{index}:v:0]fps=30,settb=1/30000,setpts=PTS-STARTPTS,setsar=1[v{index}]"
        )
        filter_parts.append(
            f"[{index}:a:0]aresample=48000:async=1:first_pts=0,asetpts=PTS-STARTPTS[a{index}]"
        )
        concat_inputs.extend([f"[v{index}]", f"[a{index}]"])

    filter_parts.append(
        "".join(concat_inputs)
        + f"concat=n={len(clips)}:v=1:a=1[vout][aout]"
    )

    command.extend([
        "-filter_complex", ";".join(filter_parts),
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
        "-r", "30", "-fps_mode", "cfr", "-video_track_timescale", "30000",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-max_muxing_queue_size", "8192",
        "-avoid_negative_ts", "make_zero",
        "-movflags", "+faststart",
        str(target),
    ])
    return command


def validate_media_file(source: Path, log: Callable[[str], None], cancel_event: threading.Event | None = None) -> None:
    """Decode the complete output once to detect truncated or corrupt streams."""
    log("Eindvideo volledig controleren op beeld- en geluidsfouten…")
    command = [
        str(FFMPEG), "-v", "error", "-xerror", "-i", str(source),
        "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-",
    ]
    run_process(command, log, cancel_event)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
class VideoCollectionView(ttk.Frame):
    """Selectable video browser with list and icon display modes.

    It intentionally exposes a small Listbox-compatible API so the existing
    conversion and merge logic can continue to work unchanged.
    """
    def __init__(self, master, app, mode_key: str, selectmode: str = "extended"):
        super().__init__(master, style="Card.TFrame")
        self.app = app
        self.mode_key = mode_key
        self.items: list[str] = []
        self._iid_by_index: list[str] = []
        self.mode_var = tk.StringVar(value=app.settings.get(mode_key, "list"))

        header = ttk.Frame(self, style="Card.TFrame")
        self.header = header
        header.pack(fill="x", pady=(0, 4))
        ttk.Label(header, text=app.t("view"), style="Card.TLabel").pack(side="left")
        self.mode_combo = ttk.Combobox(
            header, state="readonly", width=15, textvariable=self.mode_var,
            values=(app.t("list_view"), app.t("icon_view")),
        )
        self.mode_combo.pack(side="left", padx=(8, 0))
        self.mode_combo.bind("<<ComboboxSelected>>", self._mode_changed)

        body = ttk.Frame(self, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(body, show="tree", selectmode=selectmode, columns=())
        scroll = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._thumbnail_images: dict[str, tk.PhotoImage] = {}
        self._thumbnail_dir = DATA_DIR / "thumbnails"
        self._thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self._apply_saved_mode()

    def _thumbnail_path(self, video_path: Path) -> Path:
        try:
            stat = video_path.stat()
            identity = f"{video_path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
        except OSError:
            identity = str(video_path)
        digest = hashlib.sha1(identity.encode("utf-8", errors="replace")).hexdigest()
        return self._thumbnail_dir / f"{digest}.png"

    def _video_thumbnail(self, video_path: Path) -> tk.PhotoImage | None:
        """Return a cached screenshot from the video for icon view."""
        key = str(video_path)
        cached = self._thumbnail_images.get(key)
        if cached is not None:
            return cached
        if not video_path.exists() or not FFMPEG.exists():
            return None
        target = self._thumbnail_path(video_path)
        if not target.exists():
            command = [
                str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
                "-ss", "00:00:01", "-i", str(video_path), "-frames:v", "1",
                "-vf", "scale=112:64:force_original_aspect_ratio=decrease,pad=112:64:(ow-iw)/2:(oh-ih)/2",
                str(target),
            ]
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=creation_flags, timeout=20)
            except (OSError, subprocess.SubprocessError):
                target.unlink(missing_ok=True)
                return None
        try:
            image = tk.PhotoImage(file=str(target))
        except (tk.TclError, OSError):
            target.unlink(missing_ok=True)
            return None
        self._thumbnail_images[key] = image
        return image

    def _apply_saved_mode(self):
        target = self.mode_var.get()
        if target not in ("list", "icons", self.app.t("list_view"), self.app.t("icon_view")):
            target = "list"
        if target == "icons":
            self.mode_var.set(self.app.t("icon_view"))
        elif target == "list":
            self.mode_var.set(self.app.t("list_view"))
        self._render()

    def _mode_changed(self, _event=None):
        """Persist the selected view and perform the same clean restart used for language changes.

        Rebuilding a Treeview in place can leave stale Tk image and geometry state on some
        Windows systems. A quick application restart is more reliable and keeps all media,
        settings and the active page intact.
        """
        mode = "icons" if self.mode_var.get() == self.app.t("icon_view") else "list"
        self.app.settings[self.mode_key] = mode
        try:
            self.app.settings["active_deck_tab"] = self.app.notebook.index(self.app.notebook.select())
        except (AttributeError, tk.TclError):
            self.app.settings["active_deck_tab"] = 0
        save_settings(self.app.settings)
        self.mode_combo.configure(state="disabled")
        self.app.after(100, self.app.restart_application)

    def _current_mode(self) -> str:
        value = self.mode_var.get()
        return "icons" if value in ("icons", self.app.t("icon_view")) else "list"

    def _render(self, selected_indexes=None):
        if selected_indexes is None:
            selected_indexes = self.curselection()
        self.tree.delete(*self.tree.get_children())
        self._iid_by_index = []
        icon_mode = self._current_mode() == "icons"
        style = ttk.Style(self)
        style.configure(f"{self.mode_key}.Treeview", rowheight=76 if icon_mode else 28, font=("Segoe UI", 11 if icon_mode else 9))
        self.tree.configure(style=f"{self.mode_key}.Treeview")
        for index, raw in enumerate(self.items):
            path = Path(raw)
            text = path.name if icon_mode else str(path)
            thumbnail = self._video_thumbnail(path) if icon_mode else None
            iid = self.tree.insert("", "end", text=text, image=thumbnail or "")
            self._iid_by_index.append(iid)
        for index in selected_indexes:
            if 0 <= index < len(self._iid_by_index):
                self.tree.selection_add(self._iid_by_index[index])

    # Listbox-compatible API used by the rest of the application.
    def insert(self, index, value):
        value = str(value)
        if index in ("end", tk.END): self.items.append(value)
        else: self.items.insert(int(index), value)
        self._render()

    def delete(self, first, last=None):
        if not self.items: return
        if first in ("end", tk.END): first = len(self.items)-1
        first = int(first)
        if last in ("end", tk.END): last = len(self.items)-1
        if last is None: last = first
        last = int(last)
        del self.items[first:last+1]
        self._render()

    def get(self, index):
        if index in ("end", tk.END): index = len(self.items)-1
        return self.items[int(index)]

    def size(self): return len(self.items)

    def curselection(self):
        selected = set(self.tree.selection())
        return tuple(i for i, iid in enumerate(self._iid_by_index) if iid in selected)

    def selection_clear(self, first=0, last="end"):
        self.tree.selection_remove(*self.tree.selection())

    def selection_set(self, index):
        index = int(index)
        if 0 <= index < len(self._iid_by_index): self.tree.selection_add(self._iid_by_index[index])

    def activate(self, index):
        index = int(index)
        if 0 <= index < len(self._iid_by_index):
            iid = self._iid_by_index[index]
            self.tree.focus(iid); self.tree.see(iid)


class LineNumberedText(ttk.Frame):
    """Multiline editor with live line numbers and subtle alternating row guides."""

    def __init__(self, master, app: "RetroRewindApp", **text_kwargs):
        super().__init__(master, style="Card.TFrame")
        self.app = app
        self.gutter = tk.Canvas(
            self, width=52, highlightthickness=0, bd=0,
            background=app.BORDER,
        )
        self.gutter.pack(side="left", fill="y")
        self.text = tk.Text(self, **text_kwargs)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._scroll)
        self.text.configure(yscrollcommand=self._on_text_scroll)
        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self._after_id = None
        for sequence in ("<KeyRelease>", "<ButtonRelease-1>", "<MouseWheel>", "<Configure>", "<<Paste>>", "<<Cut>>", "<<Undo>>", "<<Redo>>"):
            self.text.bind(sequence, self._schedule_redraw, add="+")
        self.text.bind("<Button-4>", self._schedule_redraw, add="+")
        self.text.bind("<Button-5>", self._schedule_redraw, add="+")
        self.after_idle(self.redraw)

    def _scroll(self, *args):
        self.text.yview(*args)
        self.redraw()

    def _on_text_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self.redraw()

    def _schedule_redraw(self, _event=None):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
        self._after_id = self.after_idle(self.redraw)

    def redraw(self):
        self._after_id = None
        if not self.text.winfo_exists():
            return
        self.gutter.delete("all")
        self.gutter.configure(background=self.app.BORDER)
        # Remove old row shading and rebuild it for all current logical lines.
        self.text.tag_delete("row_even")
        self.text.tag_delete("row_odd")
        alt = self.app.BG if self.app.settings.get("theme") == "light" else self.app.CARD
        self.text.tag_configure("row_even", background=self.app.INPUT_BG)
        self.text.tag_configure("row_odd", background=alt)
        line_count = int(self.text.index("end-1c").split(".")[0])
        for line in range(1, line_count + 1):
            self.text.tag_add("row_even" if line % 2 == 0 else "row_odd", f"{line}.0", f"{line}.end+1c")

        index = self.text.index("@0,0")
        while True:
            info = self.text.dlineinfo(index)
            if info is None:
                break
            y = info[1]
            line_no = int(index.split(".")[0])
            self.gutter.create_text(
                42, y + 2, anchor="ne", text=str(line_no),
                fill=self.app.MUTED, font=("Consolas", 9),
            )
            # A light horizontal guide gives the editor a notebook/raster appearance.
            self.gutter.create_line(0, y + info[3], 52, y + info[3], fill=self.app.MUTED, stipple="gray75")
            index = self.text.index(f"{index}+1line")

class RetroRewindApp(tk.Tk):
    BG = "#F4F8FC"
    CARD = "#FFFFFF"
    TEXT = "#183247"
    MUTED = "#60788B"
    ACCENT = "#73B7E6"
    ACCENT_HOVER = "#5BA7DC"
    BORDER = "#D5E4EF"

    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME}  {APP_VERSION}  •  Created by Sacruzsa")
        self.configure(background=self.BG)
        self._set_application_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.ui_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker_running = False
        self.downloaded_files: list[Path] = []
        self.convert_files: list[Path] = []
        self.settings = load_settings()
        # Keep one canonical FFmpeg path on the application instance.
        # Sequence previews, embedded playback and conversion workers all use
        # the same bundled executable, including in PyInstaller builds.
        self.ffmpeg_path = FFMPEG
        self._ephemeral_preview_paths: set[Path] = set()
        legacy_theme_map = {
            "light": "light_studio", "dark": "dark_studio", "mixed": "classic_vcr",
            "light_vhs": "light_studio", "dark_vhs": "classic_vcr", "silver_pro": "classic_vcr",
            "classic_beige": "home_computer_1984", "blue_retro": "scifi_control_deck", "retro_pro": "dark_studio",
        }
        current_theme = self.settings.get("theme", "classic_vcr")
        self.settings["theme"] = legacy_theme_map.get(current_theme, current_theme)
        if self.settings["theme"] not in THEME_LABELS["nl"]:
            self.settings["theme"] = "classic_vcr"
        self._load_media_directories()
        self._folder_signatures: dict[str, tuple] = {}

        self._configure_window()
        self._configure_style()
        self._build_ui()
        self.after(80, self._drain_ui_queue)
        self.after(100, hide_support_files)
        self.after(250, self._startup_checks)
        self.after(1000, self._poll_media_folders)

    def _load_media_directories(self) -> None:
        defaults = {
            "downloads_dir": DOWNLOADS_DIR,
            "converted_dir": CONVERTED_DIR,
            "final_dir": FINAL_DIR,
        }
        settings_changed = False
        for key, default in defaults.items():
            raw = self.settings.get(key)
            path = Path(raw).expanduser() if raw else default
            legacy_source: Path | None = None

            # Releases up to 12.9.3 could retain a setting that points to a
            # .workspace under an older installation folder (for example a
            # former Desktop installation). Detect the layout by its structure,
            # not by the current INSTALL_DIR, so it can never be recreated.
            if is_legacy_workspace_path(path, key):
                legacy_source = path
                path = default
                self.settings[key] = str(default.resolve())
                settings_changed = True
            else:
                old_plain = INSTALL_DIR / LEGACY_MEDIA_NAMES[key]
                try:
                    if path.resolve() == old_plain.resolve():
                        legacy_source = path
                        path = default
                        self.settings[key] = str(default.resolve())
                        settings_changed = True
                except OSError:
                    pass

            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError:
                path = default
                path.mkdir(parents=True, exist_ok=True)
                self.settings[key] = str(path.resolve())
                settings_changed = True

            resolved = path.resolve()
            if legacy_source is not None:
                move_directory_contents(legacy_source, resolved)
            # Also migrate legacy folders beside the current executable.
            move_directory_contents(INSTALL_DIR / ".workspace" / LEGACY_MEDIA_NAMES[key], resolved)
            move_directory_contents(INSTALL_DIR / LEGACY_MEDIA_NAMES[key], resolved)
            setattr(self, key, resolved)

        if settings_changed:
            save_settings(self.settings)

    def _choose_settings_folder(self, key: str, variable: tk.StringVar) -> None:
        """Choose a parent directory and create the required named media folder."""
        current = Path(variable.get()).expanduser() if variable.get().strip() else INSTALL_DIR
        initial = current.parent if current.name == MEDIA_FOLDER_NAMES[key] else current
        chosen = filedialog.askdirectory(parent=self, initialdir=str(initial))
        if chosen:
            target = Path(chosen) / MEDIA_FOLDER_NAMES[key]
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError:
                messagebox.showerror(APP_NAME, self.t("folder_error", path=target), parent=self)
                return
            variable.set(str(target.resolve()))

    def restart_application(self) -> None:
        """Restart the complete process so workers and translated callbacks are recreated."""
        try:
            if getattr(sys, "frozen", False):
                command = [sys.executable]
                cwd = str(Path(sys.executable).resolve().parent)
            else:
                command = [sys.executable, str(Path(__file__).resolve())]
                cwd = str(Path(__file__).resolve().parent.parent)
            subprocess.Popen(
                command,
                cwd=cwd,
                close_fds=True,
                startupinfo=windows_startupinfo(),
                creationflags=creation_flags(),
            )
        except OSError as exc:
            messagebox.showerror(APP_NAME, str(exc), parent=self)
            return
        for preview_path in list(getattr(self, "_ephemeral_preview_paths", set())):
            try:
                preview_path.unlink(missing_ok=True)
            except OSError:
                pass
        self.destroy()

    @staticmethod
    def _ps_single_quote(value: str) -> str:
        return value.replace("'", "''")

    def _send_contact_message(
        self,
        parent: tk.Misc,
        name: str,
        subject: str,
        description: str,
        attachments: list[str],
    ) -> bool:
        """Open a user-approved email using Outlook COM or the default mail client.

        Nexus Edition never invokes PowerShell, batch files, background uploaders,
        or automatic network requests. Internet access only occurs when the user
        explicitly starts a YouTube download or sends an email.
        """
        name = name.strip()
        subject = subject.strip()
        description = description.strip()
        if not subject or not description:
            messagebox.showwarning(APP_NAME, self.t("contact_need_message"), parent=parent)
            return False

        recipient = "sacruzsa@hotmail.com"
        valid_attachments = [Path(item) for item in attachments if Path(item).is_file()]
        plain_body = (
            f"Naam:\n{name or '-'}\n\n"
            f"Onderwerp:\n{subject}\n\n"
            f"Beschrijving of suggestie:\n{description}\n\n"
            f"Bijlagen:\n{', '.join(path.name for path in valid_attachments) or '-'}\n\n"
            f"{APP_NAME} {APP_VERSION}"
        )

        if os.name == "nt" and win32com is not None:
            try:
                outlook = win32com.client.Dispatch("Outlook.Application")
                mail = outlook.CreateItem(0)
                mail.To = recipient
                mail.Subject = subject
                mail.Body = plain_body
                for path in valid_attachments:
                    mail.Attachments.Add(str(path))
                mail.Display(False)
                messagebox.showinfo(APP_NAME, self.t("contact_fallback"), parent=parent)
                return True
            except Exception:
                pass

        messagebox.showinfo(APP_NAME, self.t("contact_fallback"), parent=parent)
        if os.name == "nt":
            os.startfile("mailto:" + recipient + "?" + urllib.parse.urlencode({"subject": subject, "body": plain_body}))
        return False

    def _fit_dialog_to_screen(self, dialog: tk.Toplevel, preferred_w: int, preferred_h: int,
                              minimum_w: int = 620, minimum_h: int = 440) -> None:
        """Size and center a dialog so action buttons remain visible at any DPI."""
        dialog.update_idletasks()
        screen_w = max(640, dialog.winfo_screenwidth())
        screen_h = max(480, dialog.winfo_screenheight())
        width = min(preferred_w, max(minimum_w, screen_w - 60))
        height = min(preferred_h, max(minimum_h, screen_h - 100))
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2 - 10)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.minsize(min(minimum_w, width), min(minimum_h, height))

    def _add_creator_credit(self, window: tk.Misc) -> None:
        """Show the creator credit in the native title bar so it never overlaps controls."""
        try:
            title = window.title().strip()
            suffix = "Created by Sacruzsa"
            if suffix.lower() not in title.lower():
                window.title(f"{title}  •  {suffix}" if title else suffix)
        except (tk.TclError, AttributeError):
            pass

    def show_settings_dialog(self, initial_tab: str = "appearance") -> None:
        """Show settings in four clear pages; language selection performs a safe restart."""
        dialog = tk.Toplevel(self)
        dialog.title(self.t("settings_title"))
        dialog.transient(self)
        dialog.grab_set()
        dialog.attributes("-topmost", True)
        dialog.after(300, lambda: dialog.attributes("-topmost", False) if dialog.winfo_exists() else None)
        self._fit_dialog_to_screen(dialog, 960, 760, 760, 560)
        dialog.configure(background=self.BG)
        self._add_creator_credit(dialog)

        outer = ttk.Frame(dialog, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=self.t("settings_title"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text=self.t("settings_intro"), style="Subtitle.TLabel").pack(anchor="w", pady=(2, 14))

        selected_name = next((name for name, code in LANGUAGES.items() if code == self.language), "Nederlands")
        lang_var = tk.StringVar(value=selected_name)
        theme_key = self.settings.get("theme", "classic_vcr")
        theme_labels = THEME_LABELS.get(self.language, THEME_LABELS["nl"])
        theme_var = tk.StringVar(value=theme_labels.get(theme_key, theme_labels["classic_vcr"]))
        folder_vars = [
            ("downloads_dir", self.t("downloads_folder"), tk.StringVar(value=str(self.downloads_dir))),
            ("converted_dir", self.t("converted_folder"), tk.StringVar(value=str(self.converted_dir))),
            ("final_dir", self.t("final_folder"), tk.StringVar(value=str(self.final_dir))),
        ]

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        appearance_page = ttk.Frame(notebook, style="Card.TFrame", padding=22)
        language_page = ttk.Frame(notebook, style="Card.TFrame", padding=22)
        shortcut_page = ttk.Frame(notebook, style="Card.TFrame", padding=22)
        contact_page = ttk.Frame(notebook, style="Card.TFrame", padding=22)
        notebook.add(appearance_page, text=self.t("tab_appearance"))
        notebook.add(language_page, text=self.t("tab_language_settings"))
        notebook.add(shortcut_page, text=self.t("tab_shortcut_settings"))
        notebook.add(contact_page, text=self.t("tab_contact_settings"))
        pages = {"appearance": 0, "language": 1, "shortcut": 2, "contact": 3}
        notebook.select(pages.get(initial_tab, 0))

        ttk.Label(appearance_page, text=self.t("appearance"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(appearance_page, text=self.t("appearance_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 12))
        theme_row = ttk.Frame(appearance_page, style="Card.TFrame")
        theme_row.pack(fill="x")
        ttk.Label(theme_row, text=self.t("theme"), style="Card.TLabel", width=22).pack(side="left")
        theme_combo = ttk.Combobox(theme_row, textvariable=theme_var, values=tuple(theme_labels.values()), state="readonly", width=34)
        theme_combo.pack(side="left", fill="x", expand=True)
        theme_description_var = tk.StringVar()
        def update_theme_description(_event=None) -> None:
            selected_key = {label: key for key, label in theme_labels.items()}.get(theme_var.get(), "classic_vcr")
            descriptions = THEME_DESCRIPTIONS.get(self.language) or THEME_DESCRIPTIONS["nl"]
            theme_description_var.set(descriptions.get(selected_key, THEME_DESCRIPTIONS["nl"].get(selected_key, "")))
        theme_combo.bind("<<ComboboxSelected>>", update_theme_description)
        update_theme_description()
        ttk.Label(appearance_page, textvariable=theme_description_var, style="Card.TLabel", wraplength=650).pack(anchor="w", pady=(10, 0))
        ttk.Separator(appearance_page).pack(fill="x", pady=18)
        ttk.Label(appearance_page, text=self.t("folders"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(appearance_page, text=self.t("folders_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 8))
        folder_grid = ttk.Frame(appearance_page, style="Card.TFrame")
        folder_grid.pack(fill="x")
        folder_grid.columnconfigure(1, weight=1)
        for row, (key, label, variable) in enumerate(folder_vars):
            ttk.Label(folder_grid, text=label, style="Card.TLabel", width=22).grid(row=row, column=0, sticky="w", pady=6)
            ttk.Entry(folder_grid, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=6)
            ttk.Button(folder_grid, text=self.t("choose_folder"), command=lambda k=key, v=variable: self._choose_settings_folder(k, v)).grid(row=row, column=2, pady=6)
            ttk.Button(folder_grid, text=self.t("open_folder"), command=lambda v=variable: open_in_explorer(Path(v.get()))).grid(row=row, column=3, padx=(8, 0), pady=6)

        ttk.Label(language_page, text=self.t("language_title"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(language_page, text=self.t("language_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 18))
        language_combo = ttk.Combobox(language_page, textvariable=lang_var, values=list(LANGUAGES), state="readonly", width=34)
        language_combo.pack(anchor="w")
        ttk.Label(language_page, text=self.t("language_instant"), style="Card.TLabel", wraplength=650).pack(anchor="w", pady=(12, 0))

        ttk.Label(shortcut_page, text=self.t("shortcut_title"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(shortcut_page, text=self.t("shortcut_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 18))
        ttk.Button(shortcut_page, text=self.t("create_shortcut"), style="Accent.TButton", command=self.show_shortcut_dialog).pack(anchor="w")

        # Contact form is directly embedded in the Contact settings tab.
        contact_page.columnconfigure(0, weight=1)
        contact_page.rowconfigure(5, weight=1)
        contact_name_var = tk.StringVar()
        contact_subject_var = tk.StringVar()
        contact_attachments: list[str] = []
        ttk.Label(contact_page, text=self.t("contact_title"), style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(contact_page, text=self.t("contact_name"), style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(14, 2))
        ttk.Entry(contact_page, textvariable=contact_name_var).grid(row=2, column=0, sticky="ew")
        ttk.Label(contact_page, text=self.t("contact_subject"), style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 2))
        ttk.Entry(contact_page, textvariable=contact_subject_var).grid(row=4, column=0, sticky="ew")
        message_frame = ttk.Frame(contact_page, style="Card.TFrame")
        message_frame.grid(row=5, column=0, sticky="nsew", pady=(10, 0))
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(1, weight=1)
        ttk.Label(message_frame, text=self.t("contact_message"), style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 2))
        contact_message = tk.Text(message_frame, height=8, wrap="word", bg=self.INPUT_BG, fg=self.TEXT, insertbackground=self.TEXT, relief="solid", bd=1)
        contact_message.grid(row=1, column=0, sticky="nsew")
        ttk.Label(contact_page, text=self.t("contact_images"), style="Card.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 2))
        contact_file_list = tk.Listbox(contact_page, height=3, bg=self.INPUT_BG, fg=self.TEXT, selectbackground=self.ACCENT)
        contact_file_list.grid(row=7, column=0, sticky="ew")

        contact_tools = ttk.Frame(contact_page, style="Card.TFrame")
        contact_tools.grid(row=8, column=0, sticky="ew", pady=(6, 0))
        def add_contact_files() -> None:
            chosen = filedialog.askopenfilenames(
                parent=dialog,
                title=self.t("add_files"),
                filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), (self.t("all_files"), "*.*")],
            )
            for item in chosen:
                if item not in contact_attachments:
                    contact_attachments.append(item)
                    contact_file_list.insert("end", Path(item).name)
        def remove_contact_files() -> None:
            for index in reversed(contact_file_list.curselection()):
                contact_attachments.pop(index)
                contact_file_list.delete(index)
        ttk.Button(contact_tools, text=self.t("add_files"), command=add_contact_files).pack(side="left")
        ttk.Button(contact_tools, text=self.t("remove_selected"), command=remove_contact_files).pack(side="left", padx=8)
        def send_embedded_contact() -> None:
            sent = self._send_contact_message(
                dialog,
                contact_name_var.get(),
                contact_subject_var.get(),
                contact_message.get("1.0", "end-1c"),
                contact_attachments,
            )
            if sent:
                contact_name_var.set("")
                contact_subject_var.set("")
                contact_message.delete("1.0", "end")
                contact_attachments.clear()
                contact_file_list.delete(0, "end")
        ttk.Button(contact_tools, text=self.t("send"), style="Accent.TButton", command=send_embedded_contact).pack(side="right")

        def apply_paths_and_theme() -> bool:
            new_paths: dict[str, str] = {}
            for key, _, variable in folder_vars:
                path = Path(variable.get()).expanduser()
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except OSError:
                    messagebox.showerror(APP_NAME, self.t("folder_error", path=path), parent=dialog)
                    return False
                new_paths[key] = str(path.resolve())
            self.settings.update(new_paths)
            self.settings["theme"] = {label: key for key, label in theme_labels.items()}.get(theme_var.get(), "classic_vcr")
            save_settings(self.settings)
            self._load_media_directories()
            return True

        def language_changed(_event=None) -> None:
            code = LANGUAGES.get(lang_var.get(), "nl")
            if code == self.language:
                return
            if not apply_paths_and_theme():
                return
            self.settings["language"] = code
            save_settings(self.settings)
            dialog.grab_release()
            dialog.destroy()
            self.after(80, self.restart_application)

        language_combo.bind("<<ComboboxSelected>>", language_changed)

        def save_and_close() -> None:
            if not apply_paths_and_theme():
                return
            dialog.grab_release()
            dialog.destroy()
            # A complete restart is intentionally used here. Rebuilding only the
            # themed widgets could leave stale Tk references in the Game Video page.
            self.after(80, self.restart_application)

        actions = ttk.Frame(outer, style="App.TFrame")
        actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text=self.t("cancel"), command=dialog.destroy).pack(side="right")
        ttk.Button(actions, text=self.t("save"), style="Accent.TButton", command=save_and_close).pack(side="right", padx=8)

    def show_contact_dialog(self) -> None:
        """Compatibility entry point: open the integrated Contact settings page."""
        self.show_settings_dialog("contact")

    def _set_application_icon(self) -> None:
        """Use the RetroRewind artwork as the window and taskbar icon."""
        try:
            icon_png = resource_path("assets/RetroRewind Trailer Creator.png")
            if icon_png.exists():
                self._app_icon = tk.PhotoImage(file=str(icon_png))
                self.iconphoto(True, self._app_icon)
            if os.name == "nt":
                icon_ico = resource_path("assets/RetroRewind Trailer Creator.ico")
                if icon_ico.exists():
                    self.iconbitmap(default=str(icon_ico))
        except (tk.TclError, OSError):
            pass

    def _configure_window(self) -> None:
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(1120, max(820, screen_w - 80))
        height = min(860, max(650, screen_h - 100))
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(min(820, screen_w), min(650, screen_h))

    def _apply_palette(self) -> None:
        """Apply one of eight distinct VCR and eighties-inspired interface skins."""
        theme = self.settings.get("theme", "classic_vcr")
        palettes = {
            "classic_vcr": dict(BG="#111315", CARD="#222426", TEXT="#F1EFE8", MUTED="#AAA89F", HEADER_TEXT="#F7F4EA", HEADER_MUTED="#BBB7AC", ACCENT="#4D9A63", ACCENT_HOVER="#65B77A", BORDER="#4B4E50", INPUT_BG="#111719", LOG_BG="#06120A", PANEL_BG="#1C1E20", PANEL_TEXT="#F1EFE8", PANEL_MUTED="#B5B1A6", METAL_DARK="#0D0F10", METAL_MID="#35383A", BUTTON_TEXT="#F4F1E8", TAB_BG="#292C2E", TAB_SELECTED="#101213", REC="#D7342C", DISPLAY_BG="#06130A", DISPLAY_FG="#72FF78", LED_RED="#FF3A2F", LED_AMBER="#FFB12E"),
            "neon_video_club": dict(BG="#100A1C", CARD="#1B1030", TEXT="#F8EFFF", MUTED="#B9A5D1", HEADER_TEXT="#FFF4FF", HEADER_MUTED="#CEB5DE", ACCENT="#00D7FF", ACCENT_HOVER="#5CE8FF", BORDER="#6C2BA1", INPUT_BG="#130B22", LOG_BG="#090516", PANEL_BG="#171027", PANEL_TEXT="#F7EFFF", PANEL_MUTED="#C6ACDA", METAL_DARK="#080510", METAL_MID="#291742", BUTTON_TEXT="#FFF5FF", TAB_BG="#24133B", TAB_SELECTED="#10071D", REC="#FF2B9B", DISPLAY_BG="#080019", DISPLAY_FG="#36DDFF", LED_RED="#FF2B9B", LED_AMBER="#B46BFF"),
            "arcade_recorder": dict(BG="#070808", CARD="#111313", TEXT="#F7F7ED", MUTED="#AEB2A8", HEADER_TEXT="#FFF7C7", HEADER_MUTED="#C8C8A6", ACCENT="#22DD55", ACCENT_HOVER="#55F477", BORDER="#3D4540", INPUT_BG="#080B09", LOG_BG="#030703", PANEL_BG="#0D1010", PANEL_TEXT="#F5F5E9", PANEL_MUTED="#B5B8A9", METAL_DARK="#020303", METAL_MID="#252929", BUTTON_TEXT="#F6F6EA", TAB_BG="#171B1A", TAB_SELECTED="#050606", REC="#F13A2F", DISPLAY_BG="#020B02", DISPLAY_FG="#31F15D", LED_RED="#FF3C2F", LED_AMBER="#FFD234"),
            "home_computer_1984": dict(BG="#C9B994", CARD="#E5D7B7", TEXT="#241D13", MUTED="#675A43", HEADER_TEXT="#271F14", HEADER_MUTED="#6C5E46", ACCENT="#557A3C", ACCENT_HOVER="#729851", BORDER="#9B8965", INPUT_BG="#F5EBCF", LOG_BG="#102013", PANEL_BG="#C1AE84", PANEL_TEXT="#211A11", PANEL_MUTED="#655943", METAL_DARK="#9A8763", METAL_MID="#D5C49E", BUTTON_TEXT="#241C12", TAB_BG="#B5A17A", TAB_SELECTED="#F0E2C2", REC="#B8382E", DISPLAY_BG="#0A160D", DISPLAY_FG="#71EF72", LED_RED="#C93930", LED_AMBER="#D79B2E"),
            "scifi_control_deck": dict(BG="#07151E", CARD="#0B2431", TEXT="#DFF8FF", MUTED="#82B6C8", HEADER_TEXT="#E9FBFF", HEADER_MUTED="#91C6D5", ACCENT="#00BEEA", ACCENT_HOVER="#39D6FA", BORDER="#15536A", INPUT_BG="#071A24", LOG_BG="#031216", PANEL_BG="#09202B", PANEL_TEXT="#E3FAFF", PANEL_MUTED="#86BBCB", METAL_DARK="#041019", METAL_MID="#113644", BUTTON_TEXT="#E6FBFF", TAB_BG="#0D2C39", TAB_SELECTED="#04141D", REC="#EF3D31", DISPLAY_BG="#06131A", DISPLAY_FG="#FF9D31", LED_RED="#FF4438", LED_AMBER="#FF9D31"),
            "detective_night": dict(BG="#081619", CARD="#10272B", TEXT="#E9F0EC", MUTED="#91AAA6", HEADER_TEXT="#F1F6F2", HEADER_MUTED="#9FB5B1", ACCENT="#D39A2F", ACCENT_HOVER="#E6B551", BORDER="#27484C", INPUT_BG="#091B1F", LOG_BG="#06110E", PANEL_BG="#0D2226", PANEL_TEXT="#EDF3EF", PANEL_MUTED="#9EB2AE", METAL_DARK="#061113", METAL_MID="#183438", BUTTON_TEXT="#ECF2EE", TAB_BG="#153034", TAB_SELECTED="#071719", REC="#C94135", DISPLAY_BG="#07120E", DISPLAY_FG="#F2B13F", LED_RED="#E34538", LED_AMBER="#F2B13F"),
            "light_studio": dict(BG="#E9EBED", CARD="#F8F9FA", TEXT="#16191B", MUTED="#5A6064", HEADER_TEXT="#141719", HEADER_MUTED="#596065", ACCENT="#397F55", ACCENT_HOVER="#55A171", BORDER="#B5BABD", INPUT_BG="#FFFFFF", LOG_BG="#0C2116", PANEL_BG="#DADDE0", PANEL_TEXT="#15181A", PANEL_MUTED="#51585C", METAL_DARK="#C3C7CA", METAL_MID="#E7E9EA", BUTTON_TEXT="#141719", TAB_BG="#D2D6D8", TAB_SELECTED="#FFFFFF", REC="#C9342C", DISPLAY_BG="#0A170E", DISPLAY_FG="#5BEB6A", LED_RED="#EA3D33", LED_AMBER="#E8A536"),
            "dark_studio": dict(BG="#151719", CARD="#24272A", TEXT="#F0F2F3", MUTED="#A4AAAE", HEADER_TEXT="#F7F8F8", HEADER_MUTED="#B2B7BA", ACCENT="#4E8EBB", ACCENT_HOVER="#69A7D0", BORDER="#454A4D", INPUT_BG="#171A1D", LOG_BG="#081017", PANEL_BG="#1E2124", PANEL_TEXT="#F2F3F4", PANEL_MUTED="#ADB2B5", METAL_DARK="#101214", METAL_MID="#313538", BUTTON_TEXT="#F3F4F5", TAB_BG="#292D30", TAB_SELECTED="#111315", REC="#D63831", DISPLAY_BG="#071018", DISPLAY_FG="#78C8FF", LED_RED="#F04439", LED_AMBER="#D6A33E"),
        }
        p = palettes.get(theme, palettes["classic_vcr"])
        for key, value in p.items():
            setattr(self, key, value)
        self.DISPLAY_BG = p.get("DISPLAY_BG", "#06130A")
        self.DISPLAY_FG = p.get("DISPLAY_FG", "#72FF78")
        self.LED_RED = p.get("LED_RED", "#FF3A2F")
        self.LED_AMBER = p.get("LED_AMBER", "#FFB12E")
        self.LEVEL_GREEN = "#58E36C"
        self.LEVEL_YELLOW = "#F2D33C"
        self.LEVEL_RED = "#F0493E"
        self.configure(background=self.BG)

    def _configure_style(self) -> None:
        self._apply_palette()
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("App.TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.CARD)
        style.configure("TLabel", background=self.BG, foreground=self.HEADER_TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=self.CARD, foreground=self.TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.BG, foreground=self.HEADER_TEXT, font=("Segoe UI Semibold", 22))
        style.configure("Subtitle.TLabel", background=self.BG, foreground=self.HEADER_MUTED, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.CARD, foreground=self.TEXT, font=("Segoe UI Semibold", 12))
        style.configure("TButton", font=("Segoe UI Semibold", 10), padding=(13, 9), background=self.METAL_MID, foreground=self.BUTTON_TEXT, borderwidth=1)
        style.map("TButton", background=[("active", self.ACCENT_HOVER), ("disabled", self.BORDER)], foreground=[("disabled", self.MUTED)])
        style.configure("Accent.TButton", background=self.ACCENT, foreground="#FFFFFF" if self.settings.get("theme") not in {"light_studio", "home_computer_1984"} else "#111315")
        style.map("Accent.TButton", background=[("active", self.ACCENT_HOVER), ("disabled", "#C9DCE8")])
        style.configure("Danger.TButton", background="#9A4D55" if self.settings.get("theme") in {"classic_vcr", "neon_video_club", "arcade_recorder", "scifi_control_deck", "detective_night", "dark_studio"} else "#F9E5E5", foreground="#FFFFFF" if self.settings.get("theme") in {"classic_vcr", "neon_video_club", "arcade_recorder", "scifi_control_deck", "detective_night", "dark_studio"} else "#743737")
        style.map("Danger.TButton", background=[("active", "#F2CECE")])
        style.configure("Transport.TButton", font=("Segoe UI Symbol", 12, "bold"), padding=(12, 8), background=self.METAL_MID, foreground=self.BUTTON_TEXT, borderwidth=1, relief="raised")
        style.map("Transport.TButton", background=[("active", "#65696B"), ("pressed", "#17191B")], foreground=[("disabled", "#777777")])
        style.configure("Record.TButton", font=("Segoe UI Semibold", 10), padding=(13, 8), background="#7D2824", foreground="#FFFFFF", borderwidth=1)
        style.map("Record.TButton", background=[("active", "#A33B34"), ("pressed", "#5F1916")])
        style.configure("VCR.TNotebook", background=self.METAL_DARK, borderwidth=2, relief="sunken")
        # The notebook remains as an internal page container, while its tabs are hidden.
        # Navigation is handled by the VCR transport panel below.
        style.configure("VCR.Hidden.TNotebook", background=self.METAL_DARK, borderwidth=2, relief="sunken")
        style.layout("VCR.Hidden.TNotebook.Tab", [])
        style.configure("VCR.TNotebook.Tab", font=("Consolas", 10, "bold"), padding=(18, 9), background=self.TAB_BG, foreground=self.PANEL_TEXT, borderwidth=1)
        style.map("VCR.TNotebook.Tab", background=[("selected", self.TAB_SELECTED), ("active", self.ACCENT_HOVER)], foreground=[("selected", self.DISPLAY_FG)])
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9), padding=(14, 8), background=self.METAL_MID, foreground=self.BUTTON_TEXT, borderwidth=1)
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.CARD), ("active", self.ACCENT_HOVER)],
            font=[("selected", ("Segoe UI Semibold", 12)), ("!selected", ("Segoe UI", 9))],
        )
        style.configure("Horizontal.TProgressbar", troughcolor=self.BORDER, background=self.ACCENT, bordercolor=self.BORDER)
        style.configure("TCombobox", fieldbackground=self.INPUT_BG, background=self.CARD, foreground=self.TEXT, arrowcolor=self.TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", self.INPUT_BG)], foreground=[("readonly", self.TEXT)])
        style.configure("Treeview", background=self.INPUT_BG, fieldbackground=self.INPUT_BG, foreground=self.TEXT, bordercolor=self.BORDER)
        style.map("Treeview", background=[("selected", self.ACCENT)], foreground=[("selected", "#102D42")])
        style.configure("TEntry", fieldbackground=self.INPUT_BG, foreground=self.TEXT)

    def t(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["nl"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _build_ui(self) -> None:
        self.language = self.settings.get("language", "nl")
        if self.language not in TRANSLATIONS:
            self.language = "nl"
        self.shortcut_var = tk.StringVar(value=str(desktop_path()))
        self.main_root = ttk.Frame(self, style="App.TFrame", padding=(18, 14, 18, 14))
        self.main_root.pack(fill="both", expand=True)
        self.main_root.columnconfigure(0, weight=1)
        self.main_root.rowconfigure(2, weight=1)
        self._ui_rebuild_job = None
        self._ui_rebuilding = False
        self._render_ui()

    def _build_vcr_header(self) -> None:
        """Build the fixed VCR display panel."""
        shell = tk.Frame(self.main_root, bg=self.PANEL_BG, bd=3, relief="raised", padx=14, pady=10)
        shell.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        shell.columnconfigure(1, weight=1)

        brand = tk.Frame(shell, bg=self.PANEL_BG)
        brand.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0, 14))
        tk.Label(brand, text="RETROREWIND", bg=self.PANEL_BG, fg=self.PANEL_TEXT, font=("Arial Black", 16)).pack(anchor="w")
        tk.Label(brand, text="VHS TRAILER CREATOR", bg=self.PANEL_BG, fg=self.PANEL_MUTED, font=("Consolas", 9, "bold")).pack(anchor="w")
        ledrow = tk.Frame(brand, bg=self.PANEL_BG); ledrow.pack(anchor="w", pady=(8, 0))
        tk.Label(ledrow, text="●", bg=self.PANEL_BG, fg=self.LED_RED, font=("Segoe UI Symbol", 11)).pack(side="left")
        tk.Label(ledrow, text=" POWER", bg=self.PANEL_BG, fg=self.PANEL_MUTED, font=("Consolas", 8, "bold")).pack(side="left")

        slot = tk.Frame(shell, bg="#090A0B", bd=2, relief="sunken", height=32)
        slot.grid(row=0, column=1, sticky="ew", pady=(0, 7)); slot.grid_propagate(False)
        tk.Label(slot, text="  INSERT GAMEPLAY CASSETTE / URL  ", bg="#090A0B", fg="#77776F", font=("Consolas", 9)).place(relx=.5, rely=.5, anchor="center")

        display = tk.Frame(shell, bg=self.DISPLAY_BG, bd=2, relief="sunken", padx=12, pady=7)
        display.grid(row=1, column=1, sticky="ew")
        self.deck_display_var = tk.StringVar(value=f"VHS  SP   {APP_VERSION}   READY")
        tk.Label(display, textvariable=self.deck_display_var, bg=self.DISPLAY_BG, fg=self.DISPLAY_FG, font=("Consolas", 12, "bold"), anchor="w").pack(fill="x")

    def _build_vcr_navigation(self) -> None:
        """Place the transport navigation where the old tabs used to be."""
        transport = tk.Frame(self.main_root, bg=self.PANEL_BG, bd=2, relief="raised", padx=10, pady=7)
        transport.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        buttons = [
            ("⏮ DOWNLOAD", lambda: self._select_deck_tab(0, "REW  DOWNLOAD")),
            ("◀◀ CONVERT", lambda: self._select_deck_tab(1, "FF  CONVERT")),
            ("▶ GAME VIDEO", lambda: self._select_deck_tab(2, "PLAY  GAME VIDEO")),
            (f"▣ {self.t('preview').upper()}", self.show_final_preview),
            (f"⏏ {self.t('settings').upper()}", self.show_settings_dialog),
            (f"📖 {self.t('manual')}", self.show_instructions),
        ]
        for index, (text, command) in enumerate(buttons):
            ttk.Button(transport, text=text, style="Transport.TButton", command=command).pack(
                side="left", padx=(0 if index == 0 else 5, 0), fill="x", expand=True
            )

    def _select_deck_tab(self, index: int, display_text: str) -> None:
        try:
            self.notebook.select(index)
            self.deck_display_var.set(display_text)
        except (tk.TclError, AttributeError):
            pass

    def _deck_stop(self) -> None:
        self.cancel_event.set()
        if hasattr(self, "deck_display_var"):
            self.deck_display_var.set("STOP   READY")

    def _deck_record(self) -> None:
        try:
            self.notebook.select(2)
            self.deck_display_var.set("REC   CREATE GAME VIDEO")
            self.start_final()
        except (tk.TclError, AttributeError):
            pass

    def _render_ui(self) -> None:
        """Safely rebuild translated/theme-dependent widgets while preserving state."""
        if self._ui_rebuilding:
            return
        self._ui_rebuilding = True
        saved_urls = self.url_text.get("1.0", "end-1c") if hasattr(self, "url_text") and self.url_text.winfo_exists() else ""
        saved_convert = list(self.convert_files)
        saved_final = [self.final_list.get(i) for i in range(self.final_list.size())] if hasattr(self, "final_list") and self.final_list.winfo_exists() else []
        saved_output = self.final_output_var.get() if hasattr(self, "final_output_var") else self.settings.get("final_output", "")
        saved_log = self.log_text.get("1.0", "end-1c") if hasattr(self, "log_text") and self.log_text.winfo_exists() else ""
        saved_tab = int(self.settings.pop("active_deck_tab", 0) or 0)
        save_settings(self.settings)
        if hasattr(self, "notebook") and self.notebook.winfo_exists():
            try:
                saved_tab = self.notebook.index(self.notebook.select())
                self.notebook.unbind("<<NotebookTabChanged>>")
            except tk.TclError:
                saved_tab = 0
        for child in self.main_root.winfo_children():
            child.destroy()

        self._build_vcr_header()
        self._build_vcr_navigation()

        self.notebook = ttk.Notebook(self.main_root, style="VCR.Hidden.TNotebook")
        self.notebook.grid(row=2, column=0, sticky="nsew")
        self.download_tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=16)
        self.convert_tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=16)
        self.final_tab = ttk.Frame(self.notebook, style="Card.TFrame", padding=16)
        self.notebook.add(self.download_tab, text=self.t("tab_download"))
        self.notebook.add(self.convert_tab, text=self.t("tab_convert"))
        self.notebook.add(self.final_tab, text=self.t("tab_final"))
        self._build_download_tab(); self._build_convert_tab(); self._build_final_tab()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.after_idle(self._update_tab_sizes)

        # Progress is shown only while an operation is running, in a separate modal popup.
        self.status_var = tk.StringVar(value=self.t("ready"))
        self.progress_dialog = None
        self.popup_progress = None
        self.popup_spectrum = None
        self._spectrum_job = None
        self.popup_log_text = None
        self.log_text = tk.Text(self.main_root, height=1)
        self.log_text.grid_remove()
        if saved_log: self.log_text.insert("1.0", saved_log)
        if saved_urls: self.url_text.insert("1.0", saved_urls)
        self._set_convert_files(saved_convert)
        for item in saved_final: self.final_list.insert("end", item)
        self._update_final_count()
        if saved_output: self.final_output_var.set(saved_output)
        try:
            self.notebook.select(min(saved_tab, self.notebook.index("end") - 1))
        except tk.TclError:
            pass
        self._ui_rebuilding = False
        self.after_idle(self._update_tab_sizes)

    def _build_download_tab(self) -> None:
        ttk.Label(self.download_tab, text=self.t("video_links"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(self.download_tab, text=self.t("video_links_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 2))
        ttk.Label(self.download_tab, text=self.t("links_example"), style="Card.TLabel").pack(anchor="w", pady=(0, 8))

        self.url_editor = LineNumberedText(
            self.download_tab, self,
            height=13, wrap="none", undo=True, autoseparators=True,
            font=("Segoe UI", 10), bg=self.INPUT_BG, fg=self.TEXT,
            insertbackground=self.TEXT, selectbackground=self.ACCENT,
            relief="solid", bd=1, highlightthickness=0, padx=10, pady=10,
            spacing1=3, spacing3=3,
        )
        self.url_editor.pack(fill="both", expand=True)
        self.url_text = self.url_editor.text
        self._install_text_context_menu(self.url_text)

        buttons = ttk.Frame(self.download_tab, style="Card.TFrame")
        buttons.pack(fill="x", pady=(12, 0))
        self.download_button = ttk.Button(buttons, text=self.t("download"), style="Accent.TButton", command=self.start_download)
        self.download_button.pack(side="left")
        ttk.Button(buttons, text=self.t("paste"), command=lambda: self._paste_into_text(self.url_text)).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text=self.t("open_downloads"), command=lambda: open_in_explorer(self.downloads_dir)).pack(side="left", padx=8)
        ttk.Button(buttons, text=self.t("clear_all"), command=lambda: self.url_text.delete("1.0", "end")).pack(side="left")

    def _paste_into_text(self, widget: tk.Text) -> None:
        try:
            widget.event_generate("<<Paste>>")
            widget.focus_set()
        except tk.TclError:
            pass

    def _install_text_context_menu(self, widget: tk.Text) -> None:
        menu = tk.Menu(widget, tearoff=False, bg=self.CARD, fg=self.TEXT, activebackground=self.ACCENT, activeforeground="#102D42")
        menu.add_command(label=self.t("cut"), command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label=self.t("copy"), command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label=self.t("paste"), command=lambda: self._paste_into_text(widget))
        menu.add_separator()
        menu.add_command(label=self.t("select_all"), command=lambda: (widget.tag_add("sel", "1.0", "end-1c"), widget.mark_set("insert", "1.0"), widget.see("insert")))
        widget._context_menu = menu

        def show_menu(event):
            try:
                widget.focus_set()
                widget.mark_set("insert", f"@{event.x},{event.y}")
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return "break"

        widget.bind("<Button-3>", show_menu)
        widget.bind("<Control-Button-1>", show_menu)
        widget.bind("<Control-v>", lambda event: (self._paste_into_text(widget), "break")[1])
        widget.bind("<Control-V>", lambda event: (self._paste_into_text(widget), "break")[1])

    def _build_convert_tab(self) -> None:
        ttk.Label(self.convert_tab, text=self.t("convert_title"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(self.convert_tab, text=self.t("convert_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 8))

        # Keep both conversion views inside the main Convert page. This is an
        # embedded notebook, not a popup, so the screen stays compact and clear.
        self.convert_views = ttk.Notebook(self.convert_tab)
        self.convert_views.pack(fill="both", expand=True, pady=(4, 0))

        source_panel = ttk.Frame(self.convert_views, style="Card.TFrame", padding=12)
        output_panel = ttk.Frame(self.convert_views, style="Card.TFrame", padding=12)
        self.convert_views.add(source_panel, text=self.t("convert_source_videos"))
        self.convert_views.add(output_panel, text=self.t("converted_videos_title"))

        source_controls = ttk.Frame(source_panel, style="Card.TFrame")
        source_controls.pack(fill="x", pady=(0, 8))
        self.convert_button = ttk.Button(
            source_controls, text=self.t("convert"), style="Accent.TButton", command=self.start_convert
        )
        self.convert_button.pack(side="left")
        ttk.Button(
            source_controls, text=self.t("refresh_convert_videos"), command=self.refresh_convert_files
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            source_controls, text=self.t("clear_list"), command=self.clear_convert_list
        ).pack(side="left", padx=8)
        self.convert_count_var = tk.StringVar(value=self.t("item_count", count=0))
        ttk.Label(source_controls, textvariable=self.convert_count_var, style="Card.TLabel").pack(side="right")

        self.convert_list = VideoCollectionView(source_panel, self, "convert_view_mode")
        self.convert_list.pack(fill="both", expand=True)

        output_header = ttk.Frame(output_panel, style="Card.TFrame")
        output_header.pack(fill="x", pady=(0, 8))
        ttk.Button(
            output_header, text=f"📁 {self.t('folder_converted')}",
            command=lambda: open_in_explorer(self.converted_dir),
        ).pack(side="left")
        ttk.Button(
            output_header, text=self.t("refresh_convert_videos"), command=self.refresh_convert_files
        ).pack(side="left", padx=(8, 0))
        self.converted_count_var = tk.StringVar(value=self.t("item_count", count=0))
        ttk.Label(output_header, textvariable=self.converted_count_var, style="Card.TLabel").pack(side="right")

        self.converted_list = VideoCollectionView(output_panel, self, "converted_view_mode")
        self.converted_list.pack(fill="both", expand=True)
        ttk.Button(
            output_panel, text=self.t("open_converted"),
            command=lambda: open_in_explorer(self.converted_dir),
        ).pack(anchor="e", pady=(8, 0))

        self.refresh_convert_files()

    def open_game_video_locations(self) -> None:
        """Open both the configured Game Video folder and Retro Rewind's Steam Public folder."""
        opened: set[str] = set()
        locations = [self.final_dir, GAME_PUBLIC]
        for folder in locations:
            try:
                key = str(folder.expanduser().resolve()).lower()
            except OSError:
                key = str(folder.expanduser()).lower()
            if key in opened:
                continue
            opened.add(key)
            try:
                if folder == self.final_dir:
                    folder.mkdir(parents=True, exist_ok=True)
                if folder.exists() and folder.is_dir():
                    open_in_explorer(folder)
                else:
                    self.log(f"Game Video-map niet gevonden: {folder}")
            except OSError as exc:
                self.log(f"Kon Game Video-map niet openen: {folder} ({exc})")

    def _set_final_active_target(self, target: str) -> None:
        """Remember which Game Video collection the transport buttons should control."""
        self.final_active_target = target
        self.final_delete_target = target
        other = getattr(self, "created_final_list" if target == "clips" else "final_list", None)
        if other is not None:
            try:
                other.selection_clear(0, "end")
            except tk.TclError:
                pass

    def _build_final_tab(self) -> None:
        self.final_tab.columnconfigure(1, weight=1)
        self.final_tab.rowconfigure(3, weight=1)
        ttk.Label(self.final_tab, text=self.t("final_title"), style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(self.final_tab, text=self.t("final_help"), style="Card.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 6))

        controls = ttk.Frame(self.final_tab, style="Card.TFrame")
        controls.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        ttk.Button(controls, text=self.t("refresh_game_videos"), command=self.refresh_final_files).pack(side="left")
        ttk.Button(controls, text=self.t("open_final"), command=self.open_game_video_locations).pack(side="left", padx=(6, 0))
        self.final_count_var = tk.StringVar(value=self.t("item_count", count=0))
        ttk.Label(controls, textvariable=self.final_count_var, style="Card.TLabel").pack(side="right")

        tool_strip = ttk.Frame(self.final_tab, style="Card.TFrame")
        tool_strip.grid(row=3, column=0, sticky="ns", padx=(0, 6), pady=(6, 6))
        ttk.Button(tool_strip, text="▲", width=4, style="Transport.TButton", command=lambda: self.move_final_item(-1)).pack(pady=(2, 3), fill="x")
        ttk.Button(tool_strip, text="▼", width=4, style="Transport.TButton", command=lambda: self.move_final_item(1)).pack(pady=3, fill="x")
        ttk.Button(tool_strip, text="🗑", width=4, style="Transport.TButton", command=self.delete_final_files).pack(pady=3, fill="x")
        ttk.Button(tool_strip, text="▶", width=4, style="Transport.TButton", command=self.show_sequence_preview).pack(pady=(10, 3), fill="x")
        self.final_button = ttk.Button(tool_strip, text=self.t("record_game_video"), width=4, style="Record.TButton", command=self.start_final)
        self.final_button.pack(pady=3, fill="x")

        clip_panel = ttk.Frame(self.final_tab, style="Card.TFrame")
        clip_panel.grid(row=3, column=1, sticky="nsew", pady=(6, 6))
        clip_header = ttk.Frame(clip_panel, style="Card.TFrame")
        clip_header.pack(fill="x", pady=(0, 3))
        ttk.Label(clip_header, text=self.t("converted_preview_videos"), style="Section.TLabel").pack(side="left")
        self.final_list = VideoCollectionView(clip_panel, self, "final_view_mode")
        self.final_list.pack(fill="both", expand=True)
        self.final_list.tree.bind("<Double-Button-1>", lambda e: self.show_selected_clip_preview(), add="+")
        self.final_active_target = "clips"
        self.final_delete_target = "clips"

        output_row = ttk.Frame(self.final_tab, style="Card.TFrame")
        output_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        ttk.Label(output_row, text=self.t("save_as"), style="Card.TLabel").pack(side="left")
        default_output = self.settings.get("final_output") or str((GAME_PUBLIC if GAME_PUBLIC.exists() else self.final_dir) / "RR_Channel_Public.mp4")
        self.final_output_var = tk.StringVar(value=default_output)
        ttk.Entry(output_row, textvariable=self.final_output_var).pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(output_row, text=self.t("browse"), command=self.browse_final_output).pack(side="left")
        self.refresh_final_files()

    def _on_tab_changed(self, event=None) -> None:
        self._update_tab_sizes(event)
        try:
            selected = self.notebook.index(self.notebook.select())
            if selected == 1:
                self.refresh_convert_files()
            elif selected == 2:
                self.refresh_final_files()
        except tk.TclError:
            pass

    def _update_tab_sizes(self, _event=None) -> None:
        """Keep every tab compact so translated labels cannot reduce page height."""
        try:
            for index in range(self.notebook.index("end")):
                self.notebook.tab(index, padding=(14, 8))
        except tk.TclError:
            pass

    def toggle_progress_panel(self) -> None:
        if self.worker_running:
            self._show_progress_dialog()

    def _show_progress_dialog(self) -> None:
        if self.progress_dialog is not None and self.progress_dialog.winfo_exists():
            self.progress_dialog.deiconify(); self.progress_dialog.lift(); return
        dialog = tk.Toplevel(self); self.progress_dialog = dialog
        dialog.title(f"{APP_NAME} — {self.t('progress')}"); dialog.transient(self); dialog.grab_set()
        dialog.attributes("-topmost", True); dialog.after(300, lambda: dialog.attributes("-topmost", False))
        dialog.geometry("680x410"); dialog.minsize(540, 320); self._add_creator_credit(dialog); dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        shell = tk.Frame(dialog, bg=self.PANEL_BG, bd=4, relief="raised", padx=18, pady=16)
        shell.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(shell, text="RETROREWIND  VCR PROCESSING", bg=self.PANEL_BG, fg=self.PANEL_TEXT, font=("Consolas", 13, "bold")).pack(anchor="w")
        display = tk.Frame(shell, bg=self.DISPLAY_BG, bd=3, relief="sunken", padx=14, pady=12)
        display.pack(fill="x", pady=(10, 10))
        tk.Label(display, textvariable=self.status_var, bg=self.DISPLAY_BG, fg=self.DISPLAY_FG, font=("Consolas", 12, "bold"), anchor="w").pack(fill="x")
        self.popup_spectrum = tk.Canvas(shell, height=92, bg="#030806", highlightthickness=2, highlightbackground=self.BORDER)
        self.popup_spectrum.pack(fill="x")
        self._animate_audio_spectrum()
        self.popup_log_text = tk.Text(shell, height=12, wrap="word", font=("Consolas", 9), bg=self.DISPLAY_BG, fg=self.DISPLAY_FG, insertbackground=self.DISPLAY_FG, relief="sunken", bd=3)
        self.popup_log_text.pack(fill="both", expand=True, pady=(12, 0))
        existing = self.log_text.get("1.0", "end-1c")
        if existing: self.popup_log_text.insert("1.0", existing); self.popup_log_text.see("end")

    def _animate_audio_spectrum(self) -> None:
        """Draw a lightweight digital equalizer while media processing is active."""
        canvas = self.popup_spectrum
        if canvas is None or not canvas.winfo_exists():
            return
        width = max(canvas.winfo_width(), 420)
        height = max(canvas.winfo_height(), 80)
        canvas.delete("all")
        now = time.monotonic() * 4.2
        bars = 42
        gap = 4
        bar_width = max(3, (width - gap * (bars + 1)) / bars)
        center = height / 2
        for i in range(bars):
            envelope = 0.25 + 0.75 * abs(math.sin((i + 3) * 0.31 + now * 0.37))
            pulse = abs(math.sin(now + i * 0.47))
            amplitude = 4 + (height * 0.42) * envelope * (0.35 + 0.65 * pulse)
            x1 = gap + i * (bar_width + gap)
            x2 = x1 + bar_width
            canvas.create_rectangle(x1, center - amplitude, x2, center + amplitude,
                                    fill=self.DISPLAY_FG, outline="")
        self._spectrum_job = self.after(70, self._animate_audio_spectrum)

    def _close_progress_dialog(self) -> None:
        if self._spectrum_job is not None:
            try: self.after_cancel(self._spectrum_job)
            except tk.TclError: pass
            self._spectrum_job = None
        if self.progress_dialog is not None and self.progress_dialog.winfo_exists():
            try: self.progress_dialog.grab_release()
            except tk.TclError: pass
            self.progress_dialog.destroy()
        self.progress_dialog = self.popup_progress = self.popup_spectrum = self.popup_log_text = None

    def _request_ui_refresh(self) -> None:
        """Debounce combobox events so Tk finishes closing its popup before rebuilding."""
        if self._ui_rebuild_job is not None:
            try:
                self.after_cancel(self._ui_rebuild_job)
            except tk.TclError:
                pass
        self._ui_rebuild_job = self.after(120, self._perform_ui_refresh)

    def _perform_ui_refresh(self) -> None:
        self._ui_rebuild_job = None
        self._configure_style()
        self._render_ui()

    def change_language(self, _event=None) -> None:
        code = LANGUAGES.get(self.language_var.get(), "nl")
        if code == self.language:
            return
        self.language = code
        self.settings["language"] = code
        save_settings(self.settings)
        self._request_ui_refresh()

    def change_theme(self, _event=None) -> None:
        selected = self.theme_var.get()
        theme = {
            label: key for key, label in THEME_LABELS.get(self.language, THEME_LABELS["nl"]).items()
        }.get(selected, "classic_vcr")
        if theme == self.settings.get("theme", "classic_vcr"):
            return
        self.settings["theme"] = theme
        save_settings(self.settings)
        self._request_ui_refresh()

    def show_instructions(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title(self.t("instructions"))
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("820x700")
        dialog.minsize(680, 520)
        dialog.configure(background=self.BG)
        self._add_creator_credit(dialog)

        outer = ttk.Frame(dialog, style="Card.TFrame", padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=self.t("instructions"), style="Section.TLabel").pack(anchor="w")

        # The first visual explains where the shortcut button is and what it does.
        visual = ttk.Frame(outer, style="App.TFrame", padding=(12, 10))
        visual.pack(fill="x", pady=(10, 10))
        ttk.Label(visual, text="1", style="Title.TLabel").pack(side="left", padx=(0, 12))
        ttk.Label(
            visual,
            text="→  " + self.t("shortcut_help"),
            style="Subtitle.TLabel",
            wraplength=500,
            justify="left",
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(visual, text=self.t("shortcut"), command=self.show_shortcut_dialog).pack(side="right", padx=(12, 0))

        text_frame = ttk.Frame(outer, style="Card.TFrame")
        text_frame.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(text_frame, orient="vertical")
        text = tk.Text(
            text_frame, wrap="word", font=("Segoe UI", 11),
            bg=self.INPUT_BG, fg=self.TEXT, insertbackground=self.TEXT,
            relief="solid", bd=1, padx=16, pady=14,
            yscrollcommand=scroll.set,
        )
        scroll.configure(command=text.yview)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        text.insert("1.0", self.t("instructions_text"))
        text.tag_configure("heading", font=("Segoe UI Semibold", 12), foreground=self.ACCENT_HOVER, spacing1=8, spacing3=4)
        for line_no in range(1, int(text.index("end-1c").split(".")[0]) + 1):
            line = text.get(f"{line_no}.0", f"{line_no}.end").strip()
            if re.match(r"^\d+\.", line) or line in {"VEILIG GEBRUIK", "LEGAL USE"}:
                text.tag_add("heading", f"{line_no}.0", f"{line_no}.end")
        text.configure(state="disabled")
        ttk.Button(outer, text="OK", command=dialog.destroy).pack(anchor="e", pady=(12, 0))

    def show_shortcut_dialog(self) -> None:
        dialog = tk.Toplevel(self); dialog.title(self.t("shortcut_title")); dialog.transient(self); dialog.grab_set(); dialog.resizable(True, False); self._add_creator_credit(dialog)
        frame = ttk.Frame(dialog, style="Card.TFrame", padding=18); frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=self.t("shortcut_title"), style="Section.TLabel").pack(anchor="w")
        ttk.Label(frame, text=self.t("shortcut_help"), style="Card.TLabel").pack(anchor="w", pady=(2, 10))
        row = ttk.Frame(frame, style="Card.TFrame"); row.pack(fill="x")
        ttk.Entry(row, textvariable=self.shortcut_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text=self.t("other_location"), command=self.browse_shortcut_location).pack(side="left", padx=8)
        actions = ttk.Frame(frame, style="Card.TFrame"); actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text=self.t("cancel"), command=dialog.destroy).pack(side="right")
        ttk.Button(actions, text=self.t("create_shortcut"), style="Accent.TButton", command=lambda: self.make_shortcut(dialog)).pack(side="right", padx=8)
    # ------------------------------------------------------------------
    # Thread-safe UI helpers
    # ------------------------------------------------------------------
    def post(self, kind: str, payload: object = None) -> None:
        self.ui_queue.put((kind, payload))

    def log(self, text: str) -> None:
        self.post("log", text)

    def _drain_ui_queue(self) -> None:
        try:
            while True:
                kind, payload = self.ui_queue.get_nowait()
                if kind == "log":
                    timestamp = time.strftime("%H:%M:%S")
                    line = f"[{timestamp}] {payload}\n"
                    self.log_text.insert("end", line); self.log_text.see("end")
                    if self.popup_log_text is not None and self.popup_log_text.winfo_exists():
                        self.popup_log_text.insert("end", line); self.popup_log_text.see("end")
                elif kind == "status":
                    self.status_var.set(str(payload))
                elif kind == "refresh_final":
                    self.refresh_final_files()
                elif kind == "refresh_convert":
                    self.refresh_convert_files()
                elif kind == "busy":
                    self._set_busy(bool(payload))
                elif kind == "info":
                    messagebox.showinfo(APP_NAME, str(payload), parent=self)
                elif kind == "error":
                    messagebox.showerror(APP_NAME, str(payload), parent=self)
                elif kind == "remove_url":
                    self._remove_url_line(str(payload))
                elif kind == "set_convert_files":
                    self._set_convert_files(payload)  # type: ignore[arg-type]
                elif kind == "open_preview":
                    selected = Path(payload)
                    self.after(180, lambda selected=selected: self._open_embedded_preview(selected))
                elif kind == "open_ephemeral_preview":
                    selected = Path(payload)
                    self._ephemeral_preview_paths.add(selected)
                    self.after(180, lambda selected=selected: self._open_embedded_preview(selected, cleanup_after=True))
        except queue.Empty:
            pass
        self.after(80, self._drain_ui_queue)

    def _set_busy(self, busy: bool) -> None:
        self.worker_running = busy
        state = "disabled" if busy else "normal"
        for button in (self.download_button, self.convert_button, self.final_button):
            button.configure(state=state)
        if busy:
            self._show_progress_dialog()
        else:
            self.status_var.set(self.t("ready"))
            self._close_progress_dialog()

    def _run_worker(self, target: Callable, *args) -> None:
        if self.worker_running:
            messagebox.showwarning(APP_NAME, self.t("busy"), parent=self)
            return
        self.cancel_event.clear()
        self._set_busy(True)

        def wrapped() -> None:
            try:
                target(*args)
            except Exception as exc:
                self.log(f"FOUT: {exc}")
                self.post("error", exc)
            finally:
                self.post("busy", False)

        threading.Thread(target=wrapped, daemon=True).start()

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------
    def start_download(self) -> None:
        urls = [line.strip() for line in self.url_text.get("1.0", "end").splitlines() if line.strip()]
        urls = list(dict.fromkeys(urls))
        if not urls:
            messagebox.showwarning(APP_NAME, self.t("need_url"), parent=self)
            return
        if yt_dlp is None:
            messagebox.showerror(APP_NAME, self.t("yt_missing"), parent=self)
            return
        self._run_worker(self._download_worker, urls)

    def _download_worker(self, urls: list[str]) -> None:
        completed: list[Path] = []

        def progress_hook(data: dict) -> None:
            if data.get("status") == "downloading":
                percent = str(data.get("_percent_str", "")).strip()
                speed = str(data.get("_speed_str", "")).strip()
                self.post("status", f"Downloaden {percent} {speed}".strip())
            elif data.get("status") == "finished":
                self.log("Download klaar; bestand wordt verwerkt…")

        options = {
            "format": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
            "outtmpl": str(self.downloads_dir / "%(title).140B [%(id)s].%(ext)s"),
            "merge_output_format": "mp4",
            "ffmpeg_location": str(FFMPEG),
            "windowsfilenames": True,
            "noplaylist": True,
            "ignoreerrors": False,
            "retries": 5,
            "fragment_retries": 5,
            "continuedl": True,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": False,
        }

        with yt_dlp.YoutubeDL(options) as downloader:
            for index, url in enumerate(urls, start=1):
                self.post("status", f"Link {index} van {len(urls)} downloaden…")
                self.log(f"[{index}/{len(urls)}] Downloaden: {url}")
                before = set(self.downloads_dir.iterdir())
                try:
                    downloader.download([url])
                except Exception as exc:
                    self.log(f"Deze link is niet gedownload: {url} — {exc}")
                    continue
                after = set(self.downloads_dir.iterdir())
                new_files = sorted(
                    (p for p in after - before if p.is_file() and p.suffix.lower() not in {".part", ".ytdl"}),
                    key=lambda p: p.stat().st_mtime,
                )
                completed.extend(new_files)
                self.post("remove_url", url)
                self.log(f"Geslaagd: {url}")

        if completed:
            self.downloaded_files = completed
        self.post("refresh_convert", None)
        success_count = len(urls) - sum(1 for line in self.url_text.get("1.0", "end").splitlines() if line.strip())
        self.post("info", self.t("download_done", count=len(completed)))

    def _remove_url_line(self, url: str) -> None:
        remaining = [
            line for line in self.url_text.get("1.0", "end").splitlines()
            if line.strip() and line.strip() != url.strip()
        ]
        self.url_text.delete("1.0", "end")
        if remaining:
            self.url_text.insert("1.0", "\n".join(remaining))

    # ------------------------------------------------------------------
    # Convert
    # ------------------------------------------------------------------
    def _download_video_files(self) -> list[Path]:
        allowed = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".ts"}
        try:
            files = [
                path for path in self.downloads_dir.iterdir()
                if path.is_file() and path.suffix.lower() in allowed
            ]
        except OSError:
            return []
        return sorted(files, key=lambda path: (path.stat().st_mtime, path.name.lower()))

    def refresh_convert_files(self) -> None:
        """Refresh both source videos and already converted output videos."""
        self._set_convert_files(self._download_video_files())
        self._refresh_converted_collection()

    def _refresh_converted_collection(self) -> None:
        if not hasattr(self, "converted_list"):
            return
        files = self._converted_video_files()
        self.converted_list.delete(0, "end")
        for file in files:
            self.converted_list.insert("end", str(file))
        if hasattr(self, "converted_count_var"):
            self.converted_count_var.set(self.t("item_count", count=len(files)))

    def _set_convert_files(self, files: Iterable[Path]) -> None:
        unique: list[Path] = []
        seen: set[str] = set()
        for file in files:
            path = Path(file)
            key = str(path.resolve()).lower()
            if key not in seen and path.exists():
                seen.add(key)
                unique.append(path)
        self.convert_files = unique
        self.convert_list.delete(0, "end")
        for file in self.convert_files:
            self.convert_list.insert("end", str(file))
        if hasattr(self, "convert_count_var"):
            self.convert_count_var.set(self.t("item_count", count=len(self.convert_files)))
        if hasattr(self, "final_list"):
            self.refresh_final_files()

    def clear_convert_list(self) -> None:
        self.convert_files.clear()
        self.convert_list.delete(0, "end")
        if hasattr(self, "convert_count_var"):
            self.convert_count_var.set(self.t("item_count", count=0))

    def start_convert(self) -> None:
        self.refresh_convert_files()
        if not self.convert_files:
            return
        missing = [path for path in self.convert_files if not path.exists()]
        if missing:
            messagebox.showerror(APP_NAME, self.t("missing_file", path=missing[0]), parent=self)
            return
        self._run_worker(self._convert_worker, list(self.convert_files))

    def _convert_worker(self, files: list[Path]) -> None:
        converted: list[Path] = []
        for index, source in enumerate(files, start=1):
            self.post("status", f"Converteren {index} van {len(files)}…")
            target = unique_path(self.converted_dir / f"{safe_filename(source.stem)}_RR.mp4")
            self.log(f"[{index}/{len(files)}] Converteren: {source.name}")
            run_process(normalized_video_command(source, target), self.log, self.cancel_event)
            converted.append(target)
            self.log(f"Gemaakt: {target.name}")
            try:
                source.resolve().relative_to(self.downloads_dir.resolve())
            except (ValueError, OSError):
                pass
            else:
                try:
                    source.unlink()
                    self.log(f"Gedownloade bron verwijderd om schijfruimte te besparen: {source.name}")
                except OSError as exc:
                    self.log(f"Bronbestand kon niet worden verwijderd: {source.name} — {exc}")
        self.post("refresh_convert", None)
        self.post("refresh_final", None)
        self.post("info", self.t("convert_done", count=len(converted)))

    # ------------------------------------------------------------------
    # Final video
    # ------------------------------------------------------------------
    def _converted_video_files(self) -> list[Path]:
        try:
            return sorted(
                (p for p in self.converted_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"),
                key=lambda p: (p.stat().st_mtime, p.name.lower()),
            )
        except OSError:
            return []

    def _created_game_video_files(self) -> list[Path]:
        """Return created Game Video outputs, including configured output paths."""
        files: list[Path] = []
        seen: set[str] = set()
        def add(path: Path) -> None:
            try:
                key = str(path.expanduser().resolve()).lower()
            except OSError:
                key = str(path.expanduser()).lower()
            if key in seen or not path.exists() or not path.is_file() or path.suffix.lower() != ".mp4":
                return
            seen.add(key); files.append(path)
        if hasattr(self, "final_output_var"):
            raw = self.final_output_var.get().strip()
            if raw: add(Path(raw))
        raw = str(self.settings.get("final_output", "")).strip()
        if raw: add(Path(raw))
        try:
            for path in sorted(self.final_dir.glob("*.mp4"), key=lambda p: (p.stat().st_mtime, p.name.lower()), reverse=True):
                add(path)
        except OSError:
            pass
        if GAME_PUBLIC.exists():
            try:
                for path in sorted(GAME_PUBLIC.glob("RR_Channel_Public*.mp4"), key=lambda p: (p.stat().st_mtime, p.name.lower()), reverse=True):
                    add(path)
            except OSError:
                pass
        return files

    def refresh_final_files(self) -> None:
        """Automatically add every converted clip while preserving manual order."""
        if not hasattr(self, "final_list"):
            return
        existing = [Path(self.final_list.get(i)) for i in range(self.final_list.size())]
        available = self._converted_video_files()
        available_keys = {str(p.resolve()).lower() for p in available}
        ordered = [p for p in existing if p.exists() and str(p.resolve()).lower() in available_keys]
        known = {str(p.resolve()).lower() for p in ordered}
        ordered.extend(p for p in available if str(p.resolve()).lower() not in known)
        self.final_list.delete(0, "end")
        for path in ordered:
            self.final_list.insert("end", str(path))
        self._update_final_count()

    def _update_final_count(self) -> None:
        if hasattr(self, "final_count_var") and hasattr(self, "final_list"):
            self.final_count_var.set(self.t("item_count", count=self.final_list.size()))

    def clear_final_list(self) -> None:
        self.final_list.delete(0, "end")
        self._update_final_count()

    def add_final_files(self) -> None:
        files = filedialog.askopenfilenames(
            parent=self, initialdir=self.converted_dir, title=self.t("select_clips"),
            filetypes=[(self.t("mp4_files"), "*.mp4"), (self.t("all_video_files"), " ".join(VIDEO_EXTENSIONS))],
        )
        for file in files:
            self.final_list.insert("end", file)
        self._update_final_count()

    def move_final_item(self, direction: int) -> None:
        selection = list(self.final_list.curselection())
        if len(selection) != 1:
            return
        index = selection[0]
        destination = index + direction
        if destination < 0 or destination >= self.final_list.size():
            return
        value = self.final_list.get(index)
        self.final_list.delete(index)
        self.final_list.insert(destination, value)
        self.final_list.selection_clear(0, "end")
        self.final_list.selection_set(destination)
        self.final_list.activate(destination)
        self._update_final_count()

    def remove_final_items(self) -> None:
        for index in reversed(self.final_list.curselection()):
            self.final_list.delete(index)
        self._update_final_count()

    def delete_final_files(self) -> None:
        indexes = list(self.final_list.curselection())
        if not indexes:
            messagebox.showinfo(APP_NAME, self.t("select_item"), parent=self)
            return
        paths = [Path(self.final_list.get(index)) for index in indexes]
        question = self.t("delete_confirm", path=paths[0]) if len(paths) == 1 else self.t("delete_confirm_many", count=len(paths))
        if not messagebox.askyesno(APP_NAME, question, parent=self, icon="warning"):
            return
        deleted = 0; failed: list[tuple[Path, Exception]] = []
        for path in paths:
            try:
                path.unlink(); deleted += 1
            except FileNotFoundError:
                deleted += 1
            except OSError as exc:
                failed.append((path, exc))
        self.refresh_final_files()
        if deleted: self.log(self.t("delete_done", count=deleted))
        if failed:
            path, error = failed[0]
            messagebox.showerror(APP_NAME, self.t("delete_failed", path=path, error=error), parent=self)

    def _preview_candidates(self) -> list[Path]:
        """Return playable converted clips and created Game Videos without duplicates."""
        candidates: list[Path] = []
        seen: set[str] = set()

        def add(path: Path) -> None:
            try:
                resolved = str(path.expanduser().resolve())
            except OSError:
                resolved = str(path.expanduser())
            if resolved.lower() in seen or not path.exists() or not path.is_file():
                return
            if path.suffix.lower() not in {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".ts"}:
                return
            seen.add(resolved.lower())
            candidates.append(path)

        # The configured Game Video output always has priority.
        if hasattr(self, "final_output_var"):
            raw = self.final_output_var.get().strip()
            if raw:
                add(Path(raw))
        configured = str(self.settings.get("final_output", "")).strip()
        if configured:
            add(Path(configured))

        # Include every created Game Video from the selected final folder.
        try:
            for path in sorted(self.final_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                add(path)
        except OSError:
            pass

        # Include the current converted-video collection and folder contents.
        if hasattr(self, "final_list"):
            try:
                for index in range(self.final_list.size()):
                    add(Path(self.final_list.get(index)))
            except (tk.TclError, OSError):
                pass
        try:
            for path in sorted(self.converted_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                add(path)
        except OSError:
            pass
        return candidates

    def _selected_preview_video(self) -> Path | None:
        """Return the selected converted clip from the Game Video order list."""
        try:
            indexes = list(self.final_list.curselection())
            if indexes:
                path = Path(self.final_list.get(indexes[0])).expanduser()
                if path.exists() and path.is_file():
                    return path
        except (tk.TclError, OSError, IndexError):
            pass
        return None

    def show_selected_clip_preview(self) -> None:
        """Preview a single converted clip by double-clicking it."""
        path = self._selected_preview_video()
        if path is None:
            messagebox.showinfo(APP_NAME, self.t("select_item"), parent=self)
            return
        self._open_embedded_preview(path)

    def show_sequence_preview(self) -> None:
        """Build a fast temporary preview in the exact displayed clip order."""
        clips = [Path(self.final_list.get(index)) for index in range(self.final_list.size())]
        if not clips:
            messagebox.showinfo(APP_NAME, self.t("select_item"), parent=self)
            return
        missing = next((clip for clip in clips if not clip.exists()), None)
        if missing is not None:
            messagebox.showerror(APP_NAME, self.t("missing_clip", path=missing), parent=self)
            return
        self._run_worker(self._sequence_preview_worker, clips)

    def _sequence_preview_worker(self, clips: list[Path]) -> None:
        """Build a fresh temporary preview from every clip in the displayed order.

        A unique file is created in the application's temporary directory for
        this playback session only. It is never read from the configured final
        output and is automatically removed when the preview window closes.
        """
        import uuid

        preview_dir = TEMP_DIR / "sequence_preview"
        preview_dir.mkdir(parents=True, exist_ok=True)

        # Never reuse a previous sequence preview. Reusing a fixed filename can
        # show an older completed video when FFmpeg fails or Windows still has
        # the file open.
        output = preview_dir / f"sequence_{uuid.uuid4().hex}.mp4"
        self.post("status", self.t("sequence_preview"))

        ffmpeg = Path(getattr(self, "ffmpeg_path", FFMPEG))
        if not ffmpeg.exists():
            ffmpeg = FFMPEG
        if not ffmpeg.exists():
            raise FileNotFoundError(self.t("ffmpeg_missing", path=ffmpeg))

        # Re-encode the current list instead of using stream-copy. This ensures
        # that mixed timestamps/codecs are normalized and that the exact clips
        # currently visible in Game Video are used in the exact shown order.
        command = concat_filter_command(clips, output)
        command[0] = str(ffmpeg)
        try:
            run_process(command, self.log, self.cancel_event)
            validate_media_file(output, self.log, self.cancel_event)
        except Exception:
            try:
                output.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        self.post("open_ephemeral_preview", output)

    def show_final_preview(self) -> None:
        """Show converted clips and generated Game Videos in two separate preview tabs."""
        groups = [
            (self.t("converted_preview_videos"), self._converted_video_files()),
            (self.t("created_game_videos"), self._created_game_video_files()),
        ]
        if not any(items for _, items in groups):
            messagebox.showinfo(APP_NAME, self.t("preview_missing"), parent=self)
            return

        chooser = tk.Toplevel(self)
        chooser.title(self.t("preview_title"))
        self._add_creator_credit(chooser)
        chooser.transient(self)
        chooser.grab_set()
        self._fit_dialog_to_screen(chooser, 850, 580, 680, 460)

        frame = ttk.Frame(chooser, style="Card.TFrame", padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=self.t("preview_title"), style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        book = ttk.Notebook(frame)
        book.pack(fill="both", expand=True)
        tab_data: list[tuple[tk.Listbox, list[Path]]] = []

        for label, items in groups:
            page = ttk.Frame(book, style="Card.TFrame", padding=8)
            book.add(page, text=f"{label} ({len(items)})")
            page.rowconfigure(0, weight=1)
            page.columnconfigure(0, weight=1)
            scroll = ttk.Scrollbar(page, orient="vertical")
            lb = tk.Listbox(
                page, bg=self.INPUT_BG, fg=self.TEXT, selectbackground=self.ACCENT,
                activestyle="none", font=("Segoe UI", 10), yscrollcommand=scroll.set,
                exportselection=False,
            )
            scroll.configure(command=lb.yview)
            lb.grid(row=0, column=0, sticky="nsew")
            scroll.grid(row=0, column=1, sticky="ns")
            for item in items:
                lb.insert("end", item.name)
            if items:
                lb.selection_set(0)
                lb.activate(0)
            tab_data.append((lb, items))

        def open_selected(_event=None) -> None:
            try:
                index = book.index(book.select())
                lb, items = tab_data[index]
                selection = lb.curselection()
                if not selection or not items:
                    messagebox.showinfo(APP_NAME, self.t("select_item"), parent=chooser)
                    return
                path = items[selection[0]]
                if not path.exists():
                    messagebox.showerror(APP_NAME, f"Bestand niet gevonden:\n{path}", parent=chooser)
                    return
                chooser.grab_release()
                chooser.destroy()
                self.after(50, lambda selected=path: self._open_embedded_preview(selected))
            except (tk.TclError, IndexError, OSError) as exc:
                messagebox.showerror(APP_NAME, f"Preview kon niet worden geopend:\n{exc}", parent=chooser)

        for lb, _items in tab_data:
            lb.bind("<Double-Button-1>", open_selected)
            lb.bind("<Return>", open_selected)

        actions = ttk.Frame(frame, style="Card.TFrame")
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text=self.t("cancel"), command=chooser.destroy).pack(side="right")
        ttk.Button(actions, text="▶ PLAY", style="Accent.TButton", command=open_selected).pack(side="right", padx=(0, 8))

    def _open_embedded_preview(self, path: Path, cleanup_after: bool = False) -> None:
        """Play video frames with FFmpeg and synchronized WAV audio inside Tk."""
        import tempfile
        import winsound

        ffmpeg = Path(getattr(self, "ffmpeg_path", resource_path("tools/ffmpeg.exe")))
        if not ffmpeg.exists():
            ffmpeg = resource_path("tools/ffmpeg.exe")
        if not ffmpeg.exists():
            messagebox.showerror(APP_NAME, self.t("ffmpeg_missing", path=ffmpeg), parent=self)
            return

        def media_duration() -> float:
            cmd = [str(ffmpeg), "-hide_banner", "-i", str(path)]
            try:
                result = subprocess.run(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="replace",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=15,
                )
                match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr or "")
                if match:
                    return int(match.group(1))*3600 + int(match.group(2))*60 + float(match.group(3))
            except Exception:
                pass
            return 0.0

        duration = media_duration()
        dialog = tk.Toplevel(self)
        dialog.title(self.t("preview_title"))
        dialog.transient(self)
        dialog.grab_set()
        self._fit_dialog_to_screen(dialog, 960, 760, 720, 560)
        self._add_creator_credit(dialog)

        shell = tk.Frame(dialog, bg=self.PANEL_BG, bd=4, relief="raised", padx=16, pady=16)
        shell.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(shell, text="VCR  PLAYBACK PREVIEW", bg=self.PANEL_BG, fg=self.PANEL_TEXT,
                 font=("Consolas", 14, "bold")).pack(anchor="w")
        screen = tk.Label(shell, bg="#000000", bd=4, relief="sunken", anchor="center")
        screen.pack(fill="both", expand=True, pady=(12, 8))
        status = tk.StringVar(value=path.name)
        tk.Label(shell, textvariable=status, bg=self.PANEL_BG, fg=self.PANEL_TEXT,
                 font=("Consolas", 10, "bold"), anchor="w").pack(fill="x")

        timeline_row = tk.Frame(shell, bg=self.PANEL_BG)
        timeline_row.pack(fill="x", pady=(8, 2))
        elapsed_var = tk.StringVar(value="00:00")
        total_var = tk.StringVar(value=self._format_preview_time(duration))
        tk.Label(timeline_row, textvariable=elapsed_var, bg=self.PANEL_BG, fg=self.PANEL_TEXT,
                 font=("Consolas", 9)).pack(side="left")
        position_var = tk.DoubleVar(value=0.0)
        timeline = ttk.Scale(timeline_row, from_=0.0, to=max(duration, 1.0), variable=position_var)
        timeline.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(timeline_row, textvariable=total_var, bg=self.PANEL_BG, fg=self.PANEL_TEXT,
                 font=("Consolas", 9)).pack(side="right")

        controls = tk.Frame(shell, bg=self.PANEL_BG)
        controls.pack(fill="x", pady=(8, 0))
        volume_row = tk.Frame(shell, bg=self.PANEL_BG)
        volume_row.pack(fill="x", pady=(8, 0))
        tk.Label(volume_row, text="VOLUME", bg=self.PANEL_BG, fg=self.PANEL_TEXT,
                 font=("Consolas", 9, "bold")).pack(side="left")
        volume_var = tk.DoubleVar(value=80.0)
        volume_scale = ttk.Scale(volume_row, from_=0, to=100, variable=volume_var)
        volume_scale.pack(side="left", padx=(10, 0), ipadx=45)

        width, height, fps = 640, 360, 20
        frame_size = width * height * 3
        frames: queue.Queue[bytes | None] = queue.Queue(maxsize=2)
        state = {
            "process": None, "playing": False, "paused": False, "closed": False,
            "photo": None, "generation": 0, "position": 0.0, "started_at": 0.0,
            "seeking": False,
            "temp_dir": tempfile.TemporaryDirectory(prefix="rrtc_preview_"),
        }

        audio_lock = threading.Lock()

        def stop_audio() -> None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except RuntimeError:
                try: winsound.PlaySound(None, 0)
                except RuntimeError: pass

        def close_audio() -> None:
            stop_audio()

        def audio_segment_worker(seconds: float, generation: int, volume: float) -> None:
            """Create a WAV segment from the exact seek point and play it asynchronously."""
            segment = Path(state["temp_dir"].name) / f"audio_{generation}.wav"
            gain = max(0.0, min(1.0, volume / 100.0))
            command = [
                str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{max(0.0, seconds):.3f}", "-i", str(path), "-vn",
                "-af", f"volume={gain:.3f}", "-acodec", "pcm_s16le",
                "-ar", "44100", "-ac", "2", str(segment),
            ]
            try:
                result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if (result.returncode == 0 and segment.exists() and segment.stat().st_size > 44
                        and not state["closed"] and generation == state["generation"]
                        and state["playing"] and not state["paused"]):
                    stop_audio()
                    winsound.PlaySound(str(segment), winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as exc:
                if not state["closed"]:
                    try: status.set(f"Audio: {exc}")
                    except tk.TclError: pass

        def play_audio(seconds: float) -> None:
            if state["closed"] or not state["playing"] or state["paused"]:
                return
            generation = state["generation"]
            stop_audio()
            threading.Thread(
                target=audio_segment_worker,
                args=(seconds, generation, float(volume_var.get())), daemon=True,
            ).start()

        def current_position() -> float:
            if state["playing"] and not state["paused"]:
                return min(duration or 10**9, state["position"] + (time.monotonic() - state["started_at"]))
            return state["position"]

        def stop_process() -> None:
            proc = state.get("process")
            state["process"] = None
            if proc is not None:
                try:
                    proc.terminate(); proc.wait(timeout=.8)
                except Exception:
                    try: proc.kill()
                    except Exception: pass

        def clear_queue() -> None:
            while True:
                try: frames.get_nowait()
                except queue.Empty: break

        def reader(proc, generation: int) -> None:
            try:
                while not state["closed"] and generation == state["generation"]:
                    data = proc.stdout.read(frame_size) if proc.stdout else b""
                    if len(data) != frame_size:
                        break
                    if frames.full():
                        try: frames.get_nowait()
                        except queue.Empty: pass
                    try: frames.put_nowait(data)
                    except queue.Full: pass
            except Exception:
                pass
            finally:
                if generation == state["generation"]:
                    try: frames.put_nowait(None)
                    except queue.Full: pass

        def start_stream(start_at: float | None = None) -> bool:
            if start_at is None:
                start_at = state["position"]
            start_at = max(0.0, min(start_at, duration if duration > 0 else start_at))
            stop_process(); clear_queue(); state["generation"] += 1
            command = [str(ffmpeg), "-hide_banner", "-loglevel", "error", "-ss", f"{start_at:.3f}",
                       "-re", "-i", str(path), "-map", "0:v:0", "-an", "-vf",
                       f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
                       f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
                       "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1"]
            try:
                proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=frame_size*2,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            except OSError as exc:
                status.set(str(exc)); return False
            state.update(process=proc, playing=True, paused=False, position=start_at, started_at=time.monotonic())
            threading.Thread(target=reader, args=(proc, state["generation"]), daemon=True).start()
            play_audio(start_at)
            status.set(f"PLAY  {path.name}")
            return True

        def seek_to(seconds: float, resume: bool | None = None) -> None:
            seconds = max(0.0, min(seconds, duration if duration > 0 else seconds))
            was_playing = state["playing"] and not state["paused"] if resume is None else resume
            state["position"] = seconds
            position_var.set(seconds)
            state["generation"] += 1
            stop_process(); clear_queue(); close_audio()
            state["playing"] = False
            state["paused"] = not was_playing
            if was_playing:
                start_stream(seconds)
            else:
                status.set(f"PAUSE  {path.name}")

        def display_next() -> None:
            if state["closed"] or not dialog.winfo_exists():
                return
            if state["playing"] and not state["paused"]:
                latest = None
                while True:
                    try: latest = frames.get_nowait()
                    except queue.Empty: break
                if latest is None and state["process"] is not None and state["process"].poll() is not None:
                    state["position"] = duration if duration > 0 else current_position()
                    state["playing"] = False
                    close_audio(); status.set(f"STOP  {path.name}")
                elif isinstance(latest, (bytes, bytearray)):
                    ppm = f"P6\n{width} {height}\n255\n".encode("ascii") + bytes(latest)
                    try:
                        photo = tk.PhotoImage(data=ppm, format="PPM")
                        state["photo"] = photo; screen.configure(image=photo, text="")
                    except tk.TclError as exc:
                        status.set(f"Preview frame error: {exc}")
            if not state["seeking"]:
                pos = current_position()
                position_var.set(pos)
                elapsed_var.set(self._format_preview_time(pos))
            dialog.after(max(15, int(1000/fps)), display_next)

        def play() -> None:
            if not state["playing"]:
                if duration > 0 and state["position"] >= duration - .05:
                    state["position"] = 0.0
                start_stream(state["position"])
            elif state["paused"]:
                start_stream(state["position"])

        def pause() -> None:
            if state["playing"] and not state["paused"]:
                state["position"] = current_position()
                state["generation"] += 1; stop_process(); clear_queue(); close_audio()
                state["playing"] = False; state["paused"] = True
                status.set(f"PAUSE  {path.name}")

        def stop() -> None:
            state["generation"] += 1; stop_process(); clear_queue(); close_audio()
            state.update(playing=False, paused=False, position=0.0)
            position_var.set(0.0); elapsed_var.set("00:00")
            status.set(f"STOP  {path.name}")

        def rewind() -> None:
            seek_to(current_position() - 10.0)

        def forward() -> None:
            seek_to(current_position() + 10.0)

        def timeline_press(_event=None) -> None:
            state["seeking"] = True

        def timeline_release(_event=None) -> None:
            state["seeking"] = False
            seek_to(float(position_var.get()))

        def volume_changed(_value=None) -> None:
            if state["playing"] and not state["paused"]:
                pos = current_position()
                state["position"] = pos
                state["started_at"] = time.monotonic()
                play_audio(pos)

        def close_preview() -> None:
            state["closed"] = True; state["generation"] += 1
            stop_process(); clear_queue(); close_audio()
            try: state["temp_dir"].cleanup()
            except Exception: pass
            if cleanup_after:
                self._ephemeral_preview_paths.discard(path)
                try:
                    path.unlink(missing_ok=True)
                except OSError:
                    pass
            try: dialog.grab_release()
            except tk.TclError: pass
            if dialog.winfo_exists(): dialog.destroy()

        timeline.bind("<ButtonPress-1>", timeline_press)
        timeline.bind("<ButtonRelease-1>", timeline_release)
        volume_scale.configure(command=volume_changed)
        ttk.Button(controls, text="◀◀ 10s", style="Transport.TButton", command=rewind).pack(side="left")
        ttk.Button(controls, text="▶ PLAY", style="Transport.TButton", command=play).pack(side="left", padx=6)
        ttk.Button(controls, text="Ⅱ PAUSE", style="Transport.TButton", command=pause).pack(side="left")
        ttk.Button(controls, text="■ STOP", style="Transport.TButton", command=stop).pack(side="left", padx=6)
        ttk.Button(controls, text="10s ▶▶", style="Transport.TButton", command=forward).pack(side="left")
        ttk.Button(controls, text="CLOSE", style="Transport.TButton", command=close_preview).pack(side="right")
        dialog.protocol("WM_DELETE_WINDOW", close_preview)
        display_next()
        dialog.after(250, play)

    @staticmethod
    def _format_preview_time(seconds: float) -> str:
        seconds = max(0, int(seconds or 0))
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"

    def browse_final_output(self) -> None:
        # Always try the requested Retro Rewind folder first.
        initial = GAME_PUBLIC if GAME_PUBLIC.exists() else self.final_dir
        try:
            initial.mkdir(parents=True, exist_ok=True)
        except OSError:
            initial = self.final_dir
        chosen = filedialog.asksaveasfilename(
            parent=self,
            initialdir=initial,
            initialfile="RR_Channel_Public.mp4",
            title=self.t("save_final"),
            defaultextension=".mp4",
            filetypes=[(self.t("mp4_video"), "*.mp4")],
        )
        if chosen:
            self.final_output_var.set(chosen)

    def start_final(self) -> None:
        clips = [Path(self.final_list.get(index)) for index in range(self.final_list.size())]
        if not clips:
            self.add_final_files()
            clips = [Path(self.final_list.get(index)) for index in range(self.final_list.size())]
        if not clips:
            return
        missing = [clip for clip in clips if not clip.exists()]
        if missing:
            messagebox.showerror(APP_NAME, self.t("missing_clip", path=missing[0]), parent=self)
            return

        raw_output = self.final_output_var.get().strip()
        output = Path(raw_output) if raw_output else self.final_dir / "RR_Channel_Public.mp4"
        if output.suffix.lower() != ".mp4":
            output = output.with_suffix(".mp4")
            self.final_output_var.set(str(output))
        self.settings["final_output"] = str(output)
        save_settings(self.settings)
        self._run_worker(self._final_worker, clips, output)

    def _final_worker(self, clips: list[Path], output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        final_copy = self.final_dir / output.name

        with tempfile.TemporaryDirectory(prefix="rr_merge_", dir=TEMP_DIR) as temp_name:
            temp = Path(temp_name)
            normalized: list[Path] = []
            for index, clip in enumerate(clips, start=1):
                self.post("status", f"Clip voorbereiden {index} van {len(clips)}…")
                target = temp / f"clip_{index:04d}.mp4"
                self.log(f"[{index}/{len(clips)}] Normaliseren: {clip.name}")
                run_process(normalized_video_command(clip, target), self.log, self.cancel_event)
                normalized.append(target)

            temp_output = temp / "final_output.mp4"
            self.post("status", "Eindvideo samenvoegen…")
            self.log(
                "Samenvoegen met de robuuste concat-filter: iedere clip start opnieuw op "
                "tijdstip nul en beeld/audio worden volledig opnieuw opgebouwd…"
            )
            run_process(concat_filter_command(normalized, temp_output), self.log, self.cancel_event)

            self.post("status", "Eindvideo controleren…")
            validate_media_file(temp_output, self.log, self.cancel_event)

            shutil.copy2(temp_output, output)
            if output.resolve() != final_copy.resolve():
                shutil.copy2(temp_output, final_copy)

        self.log(f"Eindvideo opgeslagen: {output}")
        if output.resolve() != final_copy.resolve():
            self.log(f"Kopie in de zichtbare final-map: {final_copy}")
        self.post("info", self.t("final_done", path=output))

    # ------------------------------------------------------------------
    # Shortcut and lifecycle
    # ------------------------------------------------------------------
    def browse_shortcut_location(self) -> None:
        chosen = filedialog.askdirectory(
            parent=self,
            initialdir=self.shortcut_var.get() or desktop_path(),
            title=self.t("choose_shortcut"),
        )
        if chosen:
            self.shortcut_var.set(chosen)

    def make_shortcut(self, dialog=None) -> None:
        try:
            shortcut = create_windows_shortcut(Path(self.shortcut_var.get().strip() or desktop_path()))
            messagebox.showinfo(APP_NAME, self.t("shortcut_done", path=shortcut), parent=self)
            if dialog is not None:
                dialog.destroy()
        except Exception as exc:
            messagebox.showerror(APP_NAME, str(exc), parent=self)

    def _folder_signature(self, folder: Path, suffixes: set[str]) -> tuple:
        try:
            return tuple(sorted((p.name.lower(), p.stat().st_size, p.stat().st_mtime_ns) for p in folder.iterdir() if p.is_file() and p.suffix.lower() in suffixes))
        except OSError:
            return ()

    def _poll_media_folders(self) -> None:
        """Keep tabs synchronized with their folders, including external changes."""
        download_sig = self._folder_signature(self.downloads_dir, {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".ts"})
        converted_sig = self._folder_signature(self.converted_dir, {".mp4"})
        if self._folder_signatures.get("downloads") != download_sig:
            self._folder_signatures["downloads"] = download_sig
            if hasattr(self, "convert_list"):
                self.refresh_convert_files()
        if self._folder_signatures.get("converted") != converted_sig:
            self._folder_signatures["converted"] = converted_sig
            if hasattr(self, "final_list"):
                self.refresh_final_files()
        self.after(1200, self._poll_media_folders)

    def _startup_checks(self) -> None:
        if not FFMPEG.exists():
            messagebox.showerror(
                APP_NAME,
                self.t("ffmpeg_missing", path=FFMPEG),
                parent=self,
            )
        self.refresh_convert_files()
        self.refresh_final_files()
        self.log(f"Versie {APP_VERSION} gestart.")
        self.log(f"Thema: {self.settings.get('theme', 'light')} — taal: {self.language}")
        self.log(f"Interne data: {DATA_DIR}")
        self.log(f"Zichtbare final-map: {self.final_dir}")

    def _clear_log(self) -> None:
        self.log_text.delete("1.0", "end")
        if self.popup_log_text is not None and self.popup_log_text.winfo_exists():
            self.popup_log_text.delete("1.0", "end")

    def on_close(self) -> None:
        if self.worker_running:
            close = messagebox.askyesno(
                APP_NAME,
                self.t("close_busy"),
                parent=self,
            )
            if not close:
                return
            self.cancel_event.set()
        for preview_path in list(getattr(self, "_ephemeral_preview_paths", set())):
            try:
                preview_path.unlink(missing_ok=True)
            except OSError:
                pass
        self.destroy()


def _handle_setup_arguments() -> bool:
    """Handle silent installer actions without opening the GUI."""
    settings = load_settings()
    changed = False
    handled = False

    for argument in sys.argv[1:]:
        if argument.startswith("--set-language="):
            handled = True
            language = argument.split("=", 1)[1].strip().lower()
            if language in TRANSLATIONS:
                settings["language"] = language
                changed = True
        elif argument.startswith("--configure-media-root="):
            handled = True
            raw_root = argument.split("=", 1)[1].strip().strip('"')
            if raw_root:
                root = Path(raw_root).expanduser()
                root.mkdir(parents=True, exist_ok=True)
                for key, folder_name in MEDIA_FOLDER_NAMES.items():
                    target = root / folder_name
                    target.mkdir(parents=True, exist_ok=True)
                    previous_raw = settings.get(key)
                    if previous_raw:
                        previous = Path(previous_raw).expanduser()
                        if is_legacy_workspace_path(previous, key):
                            move_directory_contents(previous, target)
                    move_directory_contents(INSTALL_DIR / ".workspace" / LEGACY_MEDIA_NAMES[key], target)
                    move_directory_contents(INSTALL_DIR / LEGACY_MEDIA_NAMES[key], target)
                    settings[key] = str(target.resolve())
                changed = True

    if changed:
        save_settings(settings)
    return handled


if __name__ == "__main__":
    if not _handle_setup_arguments():
        RetroRewindApp().mainloop()

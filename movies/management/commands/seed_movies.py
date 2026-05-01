"""
Management command to seed sample movies with working video URLs.

This command populates the database with sample movies that have
publicly available video URLs for testing the streaming functionality.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from movies.models import Movie
from movies.tmdb import search_movie, get_poster_url, download_image
from movies.omdb import search_movie as search_omdb_movie
from movies.omdb import get_poster_url as get_omdb_poster_url
from io import BytesIO
import os

# Try to import PIL for creating thumbnail images
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Sample public videos from accessible sources
# Using videos from Pixabay, Archive.org, and other open sources
PLAYABLE_VIDEO_URLS = [
    'https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4',
    'https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4',
    'https://download.blender.org/durian/trailer/sintel_trailer-720p.mp4',
]

SAMPLE_VIDEOS = [
    {
        'url': 'https://cdn.pixabay.com/vimeo/736886/58978-2296370d.mp4',
        'title': 'Big Buck Bunny',
        'description': 'A large and lovable rabbit deals with three tiny bullies who are determined to spoil his fun. This Oscar-nominated animated short has won numerous awards for its stunning animation and heartwarming story.',
        'color': '#FF6B6B',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/736743/28652-2c0c3e3f.mp4',
        'title': 'Elephants Dream',
        'description': "The world's first open movie, made entirely with open source graphics software such as Blender. A surreal tale of two characters who explore a strange machine.",
        'color': '#4ECDC4',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/735734/22556-12f6a3cc.mp4',
        'title': 'For Bigger Blazes',
        'description': 'A short film about firefighting and the courage of those who battle flames. Part of the Hoplite series showcasing Google technologies.',
        'color': '#FF8C42',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/734895/21155-a69e4ff7.mp4',
        'title': 'For Bigger Escapes',
        'description': 'An action-packed short about extreme sports and breathtaking adventures. Experience the thrill of escape in this visually stunning film.',
        'color': '#95E1D3',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/747299/34055-1d8f27fa.mp4',
        'title': 'For Bigger Fun',
        'description': 'A celebration of joy and entertainment. This short showcases the lighter side of life with vibrant colors and infectious energy.',
        'color': '#F38181',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/733893/20533-ba5e96e5.mp4',
        'title': 'For Bigger Joyrides',
        'description': 'An adrenaline-pumping ride through the most exciting roads. Experience the freedom of the open road in this breathtaking journey.',
        'color': '#AA96DA',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/732595/19383-ceb2c8db.mp4',
        'title': 'For Bigger Meltdowns',
        'description': 'A dramatic exploration of nature s most powerful forces. Witness the sheer power of volcanic eruptions and natural disasters.',
        'color': '#FCBAD3',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/748456/35203-2a8f5e8a.mp4',
        'title': 'Sintel',
        'description': 'An epic fantasy animated film from the creators of Blender. A young warrior named Sintel embarks on a quest to find a baby dragon she calls Scales.',
        'color': '#B4E7FF',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/747124/33894-3e8f7f2c.mp4',
        'title': 'Subaru Outback: On Street and Dirt',
        'description': 'A showcase of the versatile Subaru Outback navigating both urban streets and challenging off-road terrain.',
        'color': '#FFD93D',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/745322/31222-1c2a5e3b.mp4',
        'title': 'Tears of Steel',
        'description': 'A sci-fi adventure set in a post-apocalyptic future. A group of warriors and scientists fight to save humanity from deadly creatures.',
        'color': '#A8DADC',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/748456/35203-2a8f5e8a.mp4',
        'title': 'Cosmos Laundromat',
        'description': 'A lonely sheep meets a mysterious salesman and is pulled into a strange, cinematic journey across worlds.',
        'genre': 'animation',
        'rating': 7.2,
        'year': 2015,
        'duration': 12,
        'color': '#355070',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/736886/58978-2296370d.mp4',
        'title': 'Spring',
        'description': 'A shepherd girl and her dog face ancient spirits as the seasons shift in a lush fantasy world.',
        'genre': 'animation',
        'rating': 7.0,
        'year': 2019,
        'duration': 8,
        'color': '#2A9D8F',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/736743/28652-2c0c3e3f.mp4',
        'title': 'Agent 327: Operation Barbershop',
        'description': 'A secret agent follows a lead into a barbershop and finds more trouble than a simple trim.',
        'genre': 'action',
        'rating': 7.1,
        'year': 2017,
        'duration': 4,
        'color': '#8D0801',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/735734/22556-12f6a3cc.mp4',
        'title': 'Caminandes: Llamigos',
        'description': 'Koro the llama discovers that teamwork can turn a stubborn problem into a playful adventure.',
        'genre': 'comedy',
        'rating': 6.8,
        'year': 2016,
        'duration': 3,
        'color': '#F4A261',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/734895/21155-a69e4ff7.mp4',
        'title': 'Caminandes: Gran Dillama',
        'description': 'A determined llama faces a hungry obstacle in a brisk animated comedy set in Patagonia.',
        'genre': 'comedy',
        'rating': 6.9,
        'year': 2013,
        'duration': 3,
        'color': '#E76F51',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/747299/34055-1d8f27fa.mp4',
        'title': 'Glass Half',
        'description': 'Two art critics debate the meaning of a gallery piece until their argument becomes the real show.',
        'genre': 'comedy',
        'rating': 6.6,
        'year': 2015,
        'duration': 3,
        'color': '#457B9D',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/733893/20533-ba5e96e5.mp4',
        'title': 'Coffee Run',
        'description': 'A caffeine-fueled errand turns into a dreamy cascade of memory, motion, and missed chances.',
        'genre': 'romance',
        'rating': 6.4,
        'year': 2020,
        'duration': 3,
        'color': '#6D597A',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/732595/19383-ceb2c8db.mp4',
        'title': 'Sprite Fright',
        'description': 'A group of noisy teenagers enter the woods and meet tiny forest creatures with a dark sense of justice.',
        'genre': 'horror',
        'rating': 7.3,
        'year': 2021,
        'duration': 11,
        'color': '#386641',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/748456/35203-2a8f5e8a.mp4',
        'title': 'Charge',
        'description': 'In a silent future, a lone survivor races through the desert to power one last hope.',
        'genre': 'sci-fi',
        'rating': 6.7,
        'year': 2022,
        'duration': 5,
        'color': '#F77F00',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/747124/33894-3e8f7f2c.mp4',
        'title': 'Hero',
        'description': 'A compact animated adventure about courage, timing, and the strange shape of doing the right thing.',
        'genre': 'animation',
        'rating': 6.5,
        'year': 2018,
        'duration': 4,
        'color': '#9B5DE5',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/745322/31222-1c2a5e3b.mp4',
        'title': 'The Daily Dweebs',
        'description': 'A mischievous pet and a predictable routine collide in a fast, expressive animated short.',
        'genre': 'comedy',
        'rating': 6.3,
        'year': 2017,
        'duration': 2,
        'color': '#00BBF9',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/736886/58978-2296370d.mp4',
        'title': 'The Old Mill',
        'description': 'A moody animated classic about birds, weather, and the fragile shelter of an abandoned mill.',
        'genre': 'drama',
        'rating': 7.5,
        'year': 1937,
        'duration': 9,
        'color': '#264653',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/736743/28652-2c0c3e3f.mp4',
        'title': 'Night of the Living Dead',
        'description': 'Survivors barricade themselves inside a farmhouse as the dead return in this public-domain horror landmark.',
        'genre': 'horror',
        'rating': 7.8,
        'year': 1968,
        'duration': 96,
        'color': '#111111',
    },
    {
        'url': 'https://cdn.pixabay.com/vimeo/735734/22556-12f6a3cc.mp4',
        'title': 'The General',
        'description': 'A train engineer chases stolen locomotives and lost love in a silent action comedy classic.',
        'genre': 'action',
        'rating': 8.1,
        'year': 1926,
        'duration': 67,
        'color': '#6C584C',
    },
]

# Genre mapping for sample videos
GENRE_MAPPING = {
    'Big Buck Bunny': 'animation',
    'Elephants Dream': 'sci-fi',
    'For Bigger Blazes': 'action',
    'For Bigger Escapes': 'action',
    'For Bigger Fun': 'comedy',
    'For Bigger Joyrides': 'action',
    'For Bigger Meltdowns': 'drama',
    'Sintel': 'animation',
    'Subaru Outback: On Street and Dirt': 'documentary',
    'Tears of Steel': 'sci-fi',
}


def create_fallback_thumbnail(title, color):
    img = Image.new('RGB', (300, 450), color)
    draw = ImageDraw.Draw(img, 'RGBA')

    palette = [
        (255, 255, 255, 34),
        (0, 0, 0, 42),
        (255, 214, 102, 82),
        (76, 201, 240, 70),
        (247, 37, 133, 58),
    ]
    title_seed = sum(ord(char) for char in title)

    for index in range(9):
        fill = palette[(title_seed + index) % len(palette)]
        x = ((title_seed * (index + 3)) % 360) - 80
        y = ((title_seed * (index + 7)) % 520) - 80
        size = 78 + ((title_seed + index * 29) % 130)
        if index % 2:
            draw.rectangle((x, y, x + size, y + size), fill=fill)
        else:
            draw.ellipse((x, y, x + size, y + size), fill=fill)

    draw.rectangle((0, 300, 300, 450), fill=(0, 0, 0, 150))

    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        meta_font = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        title_font = ImageFont.load_default()
        meta_font = ImageFont.load_default()

    words = title.split()
    lines = []
    current_line = ''
    for word in words:
        test_line = f'{current_line} {word}'.strip()
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] <= 245 or not current_line:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    y = 318
    for line in lines[:3]:
        draw.text((26, y), line, fill=(255, 255, 255, 255), font=title_font)
        y += 32

    draw.text((26, 420), 'CineWave', fill=(255, 255, 255, 170), font=meta_font)

    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=90)
    img_io.seek(0)
    return img_io.read()


class Command(BaseCommand):
    help = 'Seed the database with sample movies with working video URLs'

    def handle(self, *args, **options):
        self.stdout.write('Seeding movies...')
        
        # Clear existing movies first
        Movie.objects.all().delete()
        self.stdout.write('Cleared existing movies')
        
        for index, video_info in enumerate(SAMPLE_VIDEOS):
            tmdb_data = None
            poster_url = None

            if settings.TMDB_API_KEY:
                try:
                    tmdb_data = search_movie(video_info['title'], year=video_info.get('year'))
                    if tmdb_data:
                        poster_url = get_poster_url(tmdb_data.get('poster_path'))
                        video_info['description'] = tmdb_data.get('overview') or video_info['description']
                        if tmdb_data.get('vote_average'):
                            video_info['rating'] = round(float(tmdb_data.get('vote_average')), 1)
                        if tmdb_data.get('release_date'):
                            try:
                                video_info['year'] = int(tmdb_data['release_date'][:4])
                            except ValueError:
                                pass
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  WARNING: TMDb lookup failed for {video_info["title"]}: {str(e)}'))

            if not tmdb_data and settings.OMDB_API_KEY:
                try:
                    omdb_data = search_omdb_movie(video_info['title'], year=video_info.get('year'))
                    if omdb_data:
                        poster_url = get_omdb_poster_url(omdb_data.get('Poster'))
                        video_info['description'] = omdb_data.get('Plot') or video_info['description']
                        if omdb_data.get('imdbRating') and omdb_data['imdbRating'] != 'N/A':
                            video_info['rating'] = round(float(omdb_data['imdbRating']), 1)
                        if omdb_data.get('Year') and omdb_data['Year'] != 'N/A':
                            try:
                                video_info['year'] = int(omdb_data['Year'][:4])
                            except ValueError:
                                pass
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  OMDb lookup failed for {video_info["title"]}: {str(e)}'))

            movie = Movie.objects.create(
                title=video_info['title'],
                description=video_info['description'],
                genre=video_info.get('genre', GENRE_MAPPING.get(video_info['title'], 'action')),
                video_url=PLAYABLE_VIDEO_URLS[index % len(PLAYABLE_VIDEO_URLS)],
                rating=round(video_info.get('rating', 6.0), 1),
                year=video_info.get('year', 2020),
                duration=video_info.get('duration', 60 + (index * 30)),
                is_featured=(index == 0),
            )

            if poster_url:
                try:
                    poster_data = download_image(poster_url)
                    filename = f"poster_{movie.title.lower().replace(' ', '_')}.jpg"
                    movie.thumbnail.save(filename, ContentFile(poster_data), save=True)
                    self.stdout.write(self.style.SUCCESS(f'  Downloaded poster for {movie.title}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  WARNING: Could not download poster for {movie.title}: {str(e)}'))

            if not movie.thumbnail and HAS_PIL and 'color' in video_info:
                try:
                    filename = f"thumbnail_{movie.title.lower().replace(' ', '_')}.jpg"
                    poster_data = create_fallback_thumbnail(movie.title, video_info['color'])
                    movie.thumbnail.save(filename, ContentFile(poster_data), save=True)
                    self.stdout.write(self.style.SUCCESS(f'  Created fallback thumbnail for {movie.title}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  WARNING: Could not create fallback thumbnail for {movie.title}: {str(e)}'))

            self.stdout.write(self.style.SUCCESS(f'Created: {movie.title} ({movie.genre})'))
        
        total = Movie.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal movies in database: {total}'))
        self.stdout.write('\nMovies are ready to play! Visit the site and click on any movie.')

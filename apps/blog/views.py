from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import status, exceptions, permissions
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, FileUploadParser

from django.db.models.query_utils import Q

from apps.blog.pagination import SmallPagination, MediumPagination, BigPagination
from apps.blog.serializer import CategorySerializers, BlogsSerializers
from apps.blog.models import Categoryes, Blogs
from apps.user_system.models import Model_users


# All categoryes
class AllCategorys (APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        categoryes = Categoryes.objects.all()
        if categoryes:
            serializer = CategorySerializers(categoryes, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "not_Found"}, status=status.HTTP_404_NOT_FOUND)


# all blogs
class AllBlogs (APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):

        if Blogs.objects.order_by("-creation").all():
            filter_blogs = Blogs.objects.filter(public=True)
            pagination = MediumPagination()
            response = pagination.paginate_queryset(filter_blogs, request)
            serializer = BlogsSerializers(response, many=True)
            return pagination.get_paginated_response(serializer.data)
        else:
            return Response({"Error": "not_Found"}, status=status.HTTP_404_NOT_FOUND)


# Blogs by category view
class BlogsByCategoryView (APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        categorys = Categoryes.objects.all()
        if categorys:
            slug = request.query_params.get("slug")
            filter_category = Categoryes.objects.filter(slug=slug)
            if filter_category:
                blogs = []
                for data in filter_category:
                    blogs.extend(Blogs.objects.filter(
                        category=data.id, public=True))

                if blogs:
                    pagination = MediumPagination()
                    response = pagination.paginate_queryset(blogs, request)
                    serializer = BlogsSerializers(response, many=True)
                    return pagination.get_paginated_response(serializer.data)

                else:
                    return Response({"erorr": "not_Found"}, status=status.HTTP_404_NOT_FOUND)

            else:
                return Response({"erorr": "not_Found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"erorr": "not_Found"}, status=status.HTTP_404_NOT_FOUND)


class BLogDetail (APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        if Blogs.objects.all():
            slug = request.query_params.get("slug")
            blog = Blogs.objects.filter(slug=slug)

            if blog:
                seiralizer = BlogsSerializers(blog, many=True)
                return Response(seiralizer.data)

            else:
                return Response({"erorr": "Este blog no existe"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"erorr": "not_Foundd"}, status=status.HTTP_404_NOT_FOUND)


class SearchBlogs (APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):

        if Blogs.objects.all():
            slug = request.query_params.get("slug")
            blogs = Blogs.objects.order_by(
                "-creation").filter(Q(title__startswith=slug), public=True)

            if blogs:
                pagination = BigPagination()
                response = pagination.paginate_queryset(blogs, request)
                serializer = BlogsSerializers(response, many=True)
                return pagination.get_paginated_response(serializer.data)

            else:
                return Response({"erorr": "not_Found"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"erorr": "not_Found"}, status=status.HTTP_404_NOT_FOUND)


# Blogs of users

@api_view(["GET"])
@permission_classes(permission_classes=[permissions.IsAuthenticated])
def BlogByUser(request):
    blogs_user = Blogs.objects.order_by("-update").filter(user=request.user.id)
    if blogs_user:
        pagination = SmallPagination()
        response = pagination.paginate_queryset(blogs_user, request)
        serializer = BlogsSerializers(response, many=True)
        return pagination.get_paginated_response(serializer.data)

    else:
        return Response({"not_Found": "404"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes(permission_classes=[permissions.IsAuthenticated])
def blogDetailByUser(request):
    slug = request.query_params.get("slug")
    filter_blog_user = Blogs.objects.filter(user=request.user.id, slug=slug)
    if filter_blog_user:
        serializer = BlogsSerializers(filter_blog_user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    else:
        return Response({"Error": "not_Found"}, status=status.HTTP_404_NOT_FOUND)


############# Isauthenticated user

@api_view(["POST"])
@permission_classes(permission_classes=[permissions.IsAuthenticated])
@parser_classes(parser_classes=[JSONParser, FormParser,FileUploadParser])
def createBlogUser(request):
    user = request.user
    category = Categoryes.objects.get(id=request.data["category"]["id"])
    blogs_titles = Blogs.objects.all()
    list_titles = []
    for data in blogs_titles:
        list_titles.append(data.title)

    if request.data["title"] in list_titles:
        return Response({"Error": "Este titulo ya existe"}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        try:
            new_blog = Blogs.objects.create(
                title=request.data["title"],
                description=request.data["description"],
                public=bool(request.data["public"]),
                category=category,
                user=user,
            )
            new_blog.save()
            return Response({"success": "Blog creado"}, status=status.HTTP_201_CREATED)
        except:
            return Response({"Error": "Parece que hubo algun error"}, status=status.HTTP_409_CONFLICT)



@api_view(["PUT"])
@permission_classes(permission_classes=[permissions.IsAuthenticated])
@parser_classes(parser_classes=[JSONParser])
def updateBlogsByUser(request):
    slug = request.query_params.get("slug")
    filter_blog_user = Blogs.objects.filter(user=request.user.id, slug=slug)
    if filter_blog_user:
        for blog in filter_blog_user:
            blog.title = request.data["title"]
            blog.slug = "slug" + str(request.data["title"])
            blog.description = request.data["description"].capitalize()
            public = str(request.data["public"]).capitalize()
            if public == "True":
                blog.public = True
            else:
                blog.public = False
            blog.save()
            return Response({"success": "update completed"}, status=status.HTTP_200_OK)

    else:
        return Response({"Error": "not_Found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(["DELETE"])
@permission_classes(permission_classes=[permissions.IsAuthenticated])
def DeleteBlogByUser (request) :
    slug = request.query_params.get("slug")
    filter_blog = Blogs.objects.filter(slug = slug)
    if len(filter_blog) != 0:
        filter_blog.delete()
        return Response ({"success":"Blog eliminado correctamente"}, status=status.HTTP_202_ACCEPTED)
    else :
        return Response ({"Error":"Error"}, status=status.http4)
    
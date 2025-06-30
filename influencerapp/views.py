from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import connection
from .models import Influencer
from .serializers import InfluencerSerializer
import tempfile, traceback, openpyxl
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie

@api_view(['GET'])
def get_all_influencers_by_region(request):
    try:
        selected_region = request.GET.get('selectedRegion', '')
        query = Influencer.objects.all()
        if selected_region:
            query = query.filter(region=selected_region)
        influencers = query.order_by('-followers')
        serializer = InfluencerSerializer(influencers, many=True)
        return Response({
            "items": serializer.data,
            "totalItems": len(serializer.data)
        })
    except Exception as e:
        return Response({"error": "Failed to fetch all influencers", "details": str(e)}, status=500)

@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_influencers(request):
    try:
        page = int(request.GET.get('page', 0))
        rows_per_page = int(request.GET.get('rowsPerPage', 10))
        order_by = request.GET.get('orderBy', 'popularity')
        order_direction = request.GET.get('orderDirection', 'desc')
        search_term = request.GET.get('searchTerm', '')
        selected_region = request.GET.get('selectedRegion', '')

        query = Influencer.objects.all()

        if selected_region:
            query = query.filter(region=selected_region)

        if search_term:
            query = query.filter(
                Q(username__icontains=search_term) |
                Q(storeName__icontains=search_term) |
                Q(region__icontains=search_term)
            )

        if order_by in ['id', 'username', 'followers', 'storeName', 'popularity', 'region']:
            if order_direction == 'asc':
                query = query.order_by(order_by)
            else:
                query = query.order_by(f'-{order_by}')
        else:
            query = query.order_by('-popularity')

        total_items = query.count()
        influencers = query[page * rows_per_page:(page + 1) * rows_per_page]
        serializer = InfluencerSerializer(influencers, many=True)

        return Response({"items": serializer.data, "totalItems": total_items})
    except Exception as e:
        return Response({"error": "Failed to fetch influencers", "details": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_influencers(request):
    try:
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "ファイルがアップロードされていません。"}, status=400)

        if not (uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls')):
            return Response({"error": "Excelファイル（.xlsx または .xls）のみ受け付けます。"}, status=400)

        # DBをTRUNCATE
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE influencers')

        # 一時ファイル保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
            for chunk in uploaded_file.chunks():
                temp_excel.write(chunk)
            temp_file_path = temp_excel.name

        wb = openpyxl.load_workbook(temp_file_path)
        sheet = wb.active

        imported_count, skipped_count = 0, 0
        errors = []
        for i, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            try:
                username = row[0].value
                followers = int(row[1].value or 0)
                storeName = row[2].value
                popularity = int(row[3].value or 0)
                region = row[4].value

                if not username:
                    skipped_count += 1
                    errors.append(f"{i}行目: ユーザー名がありません")
                    continue

                Influencer.objects.create(
                    username=username,
                    followers=followers,
                    storeName=storeName,
                    popularity=popularity,
                    region=region
                )
                imported_count += 1
            except Exception as e:
                skipped_count += 1
                errors.append(f"{i}行目: エラー - {str(e)}")

        message = f"インポート完了：成功 {imported_count}件、スキップ {skipped_count}件"
        return Response({"message": message, "errors": errors})
    except Exception as e:
        print(traceback.format_exc())
        return Response({"error": f"エラー発生: {e}"}, status=500)

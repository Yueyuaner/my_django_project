// 全局变量
let annotations = [];
let selectedAnnotationId = null;
let currentBox = null;
let isDrawing = false;
let isDragging = false;
let isResizing = false;
let resizeHandle = null;
let startX = 0;
let startY = 0;
let currentScale = 1;
let nextAnnotationId = 1;
let hasUnsavedChanges = false;

// DOM 元素
const container = document.getElementById('annotation-container');
const canvas = document.getElementById('annotation-canvas');
const image = document.getElementById('annotation-image');
const annotationList = document.getElementById('annotation-list');
const labelList = document.getElementById('label-list');
const saveButton = document.getElementById('save-annotations-btn');
const clearButton = document.getElementById('clear-annotations-btn');
const deleteButton = document.getElementById('delete-selected-btn');
const zoomInButton = document.getElementById('zoom-in-btn');
const zoomOutButton = document.getElementById('zoom-out-btn');
const resetZoomButton = document.getElementById('reset-zoom-btn');
const cursorPosition = document.getElementById('cursor-position');
const imageDimensions = document.getElementById('image-dimensions');
const noAnnotationsMessage = document.getElementById('no-annotations-message');

// 标签选择模态框
const labelModal = new bootstrap.Modal(document.getElementById('labelSelectionModal'));

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 加载完成，初始化标注功能');
    
    // 检查必要的 DOM 元素是否存在
    if (!container || !canvas || !image) {
        console.error('找不到必要的 DOM 元素:', {
            container: !!container,
            canvas: !!canvas,
            image: !!image
        });
        return;
    }
    
    // 绑定鼠标事件
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    container.addEventListener('mouseleave', handleMouseLeave);
    
    // 绑定键盘事件
    document.addEventListener('keydown', handleKeyDown);
    
    // 加载已有标注
    if (window.existingAnnotations && window.existingAnnotations.length > 0) {
        console.log('加载已有标注:', window.existingAnnotations);
        annotations = window.existingAnnotations.map(a => {
            a.id = nextAnnotationId++;
            return a;
        });
        
        // 创建标注框和列表项
        annotations.forEach(annotation => {
            createAnnotationBox(annotation);
            createAnnotationListItem(annotation);
        });
        
        // 更新标签计数
        updateLabelCounts();
        
        // 更新总标注数
        if (document.getElementById('total-annotations-count')) {
            document.getElementById('total-annotations-count').textContent = annotations.length;
        }
        
        // 更新标注状态
        const annotationStatus = document.getElementById('annotation-status');
        if (annotationStatus) {
            annotationStatus.className = 'badge bg-success';
            annotationStatus.textContent = '已保存';
        }
        
        // 初始时没有未保存的更改
        hasUnsavedChanges = false;
    } else {
        console.log('没有已有标注');
    }
    
    // 显示图片尺寸
    image.onload = function() {
        if (imageDimensions) {
            imageDimensions.textContent = `${image.naturalWidth} × ${image.naturalHeight}`;
        }
        console.log('图片加载完成:', image.naturalWidth, image.naturalHeight);
    };
    
    // 鼠标移动时显示坐标
    if (container && cursorPosition) {
        container.addEventListener('mousemove', function(e) {
            const rect = container.getBoundingClientRect();
            const x = Math.round((e.clientX - rect.left) / currentScale);
            const y = Math.round((e.clientY - rect.top) / currentScale);
            cursorPosition.textContent = `坐标: ${x}, ${y}`;
        });
    }
    
    // 绑定按钮事件
    if (zoomInButton) zoomInButton.addEventListener('click', zoomIn);
    if (zoomOutButton) zoomOutButton.addEventListener('click', zoomOut);
    if (resetZoomButton) resetZoomButton.addEventListener('click', resetZoom);
    if (clearButton) clearButton.addEventListener('click', clearAnnotations);
    if (saveButton) saveButton.addEventListener('click', saveAnnotations);
    if (deleteButton) deleteButton.addEventListener('click', deleteSelectedAnnotation);
    
    // 绑定标签选择事件
    if (labelList) {
        const labelItems = labelList.querySelectorAll('.label-item');
        labelItems.forEach(item => {
            item.addEventListener('click', function() {
                const labelId = this.dataset.labelId;
                const labelName = this.dataset.labelName;
                const labelColor = this.dataset.labelColor;
                
                if (selectedAnnotationId !== null) {
                    // 更新选中标注的标签
                    const annotation = annotations.find(a => a.id === selectedAnnotationId);
                    if (annotation) {
                        annotation.label_id = labelId;
                        annotation.label_name = labelName;
                        annotation.label_color = labelColor;
                        
                        // 更新标注框和列表项
                        updateAnnotationBox(annotation);
                        createAnnotationListItem(annotation);
                        
                        // 更新标签计数
                        updateLabelCounts();
                    }
                }
            });
        });
    }
    
    // 绑定模态框中的标签选择事件
    const modalLabelItems = document.querySelectorAll('#labelSelectionModal .label-item');
    modalLabelItems.forEach(item => {
        item.addEventListener('click', function() {
            const labelId = this.dataset.labelId;
            const labelName = this.dataset.labelName;
            const labelColor = this.dataset.labelColor;
            
            // 为临时标注设置标签
            if (currentAnnotation) {
                currentAnnotation.label_id = labelId;
                currentAnnotation.label_name = labelName;
                currentAnnotation.label_color = labelColor;
                
                // 添加到标注列表
                annotations.push(currentAnnotation);
                
                // 创建标注框和列表项
                createAnnotationBox(currentAnnotation);
                createAnnotationListItem(currentAnnotation);
                
                // 更新标签计数
                updateLabelCounts();
                
                // 更新总标注数
                if (document.getElementById('total-annotations-count')) {
                    document.getElementById('total-annotations-count').textContent = annotations.length;
                }
                
                // 更新标注状态为"未保存"
                const annotationStatus = document.getElementById('annotation-status');
                if (annotationStatus) {
                    annotationStatus.className = 'badge bg-warning';
                    annotationStatus.textContent = '未保存';
                }
                
                // 标记为有未保存的更改
                hasUnsavedChanges = true;
                
                // 重置临时标注
                currentAnnotation = null;
            }
            
            // 关闭模态框
            labelModal.hide();
        });
    });
    
    // 添加离开页面前的提示
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            const message = '您有未保存的标注，确定要离开吗？';
            e.returnValue = message;
            return message;
        }
    });
    
    console.log('标注功能初始化完成');
});

// 鼠标按下事件处理
function handleMouseDown(e) {
    // 获取鼠标相对于容器的坐标
    const rect = container.getBoundingClientRect();
    startX = (e.clientX - rect.left) / currentScale;
    startY = (e.clientY - rect.top) / currentScale;
    
    // 检查是否点击了已有的标注框
    const boxes = canvas.querySelectorAll('.annotation-box');
    let clickedBox = null;
    
    boxes.forEach(box => {
        const boxRect = box.getBoundingClientRect();
        if (e.clientX >= boxRect.left && e.clientX <= boxRect.right &&
            e.clientY >= boxRect.top && e.clientY <= boxRect.bottom) {
            clickedBox = box;
        }
    });
    
    if (clickedBox) {
        // 点击了已有的框
        const id = parseInt(clickedBox.id.replace('box-', ''));
        
        // 检查是否点击了调整大小的手柄
        const handles = clickedBox.querySelectorAll('.resize-handle');
        let clickedHandle = null;
        
        handles.forEach(handle => {
            const handleRect = handle.getBoundingClientRect();
            if (e.clientX >= handleRect.left && e.clientX <= handleRect.right &&
                e.clientY >= handleRect.top && e.clientY <= handleRect.bottom) {
                clickedHandle = handle;
            }
        });
        
        if (clickedHandle) {
            // 开始调整大小
            isResizing = true;
            resizeHandle = clickedHandle.className.split(' ')[1]; // 获取方向 (nw, ne, sw, se)
            selectAnnotation(id);
        } else {
            // 开始拖动
            isDragging = true;
            selectAnnotation(id);
        }
    } else {
        // 开始绘制新框
        isDrawing = true;
        
        // 取消选中当前选中的标注
        if (selectedAnnotationId !== null) {
            deselectAnnotation();
        }
        
        // 创建新的框元素
        currentBox = document.createElement('div');
        currentBox.className = 'annotation-box drawing';
        currentBox.style.left = startX + 'px';
        currentBox.style.top = startY + 'px';
        canvas.appendChild(currentBox);
    }
}

// 鼠标移动事件处理
function handleMouseMove(e) {
    // 获取鼠标相对于容器的坐标
    const rect = container.getBoundingClientRect();
    const x = (e.clientX - rect.left) / currentScale;
    const y = (e.clientY - rect.top) / currentScale;
    
    if (isDrawing && currentBox) {
        // 计算宽度和高度
        const width = Math.abs(x - startX);
        const height = Math.abs(y - startY);
        
        // 计算左上角坐标
        const left = Math.min(x, startX);
        const top = Math.min(y, startY);
        
        // 更新框的位置和大小
        currentBox.style.left = left + 'px';
        currentBox.style.top = top + 'px';
        currentBox.style.width = width + 'px';
        currentBox.style.height = height + 'px';
    } else if (isDragging && selectedAnnotationId !== null) {
        // 拖动选中的框
        const annotation = annotations.find(a => a.id === selectedAnnotationId);
        if (annotation) {
            // 计算偏移量
            const dx = x - startX;
            const dy = y - startY;
            
            // 更新坐标
            annotation.x += dx;
            annotation.y += dy;
            
            // 确保不超出图片边界
            annotation.x = Math.max(0, Math.min(annotation.x, image.naturalWidth - annotation.width));
            annotation.y = Math.max(0, Math.min(annotation.y, image.naturalHeight - annotation.height));
            
            // 更新框的位置
            updateAnnotationBox(annotation);
            
            // 更新起始坐标
            startX = x;
            startY = y;
            
            // 更新标注状态为"未保存"
            const annotationStatus = document.getElementById('annotation-status');
            if (annotationStatus) {
                annotationStatus.className = 'badge bg-warning';
                annotationStatus.textContent = '未保存';
            }
            
            // 标记为有未保存的更改
            hasUnsavedChanges = true;
        }
    } else if (isResizing && selectedAnnotationId !== null) {
        // 调整选中框的大小
        const annotation = annotations.find(a => a.id === selectedAnnotationId);
        if (annotation) {
            // 根据不同的调整手柄计算新的位置和大小
            switch (resizeHandle) {
                case 'nw': // 左上
                    annotation.width += annotation.x - x;
                    annotation.height += annotation.y - y;
                    annotation.x = x;
                    annotation.y = y;
                    break;
                case 'ne': // 右上
                    annotation.width = x - annotation.x;
                    annotation.height += annotation.y - y;
                    annotation.y = y;
                    break;
                case 'sw': // 左下
                    annotation.width += annotation.x - x;
                    annotation.height = y - annotation.y;
                    annotation.x = x;
                    break;
                case 'se': // 右下
                    annotation.width = x - annotation.x;
                    annotation.height = y - annotation.y;
                    break;
            }
            
            // 确保宽度和高度为正值
            if (annotation.width < 0) {
                annotation.x += annotation.width;
                annotation.width = Math.abs(annotation.width);
                
                // 切换水平方向的手柄
                if (resizeHandle === 'nw') resizeHandle = 'ne';
                else if (resizeHandle === 'ne') resizeHandle = 'nw';
                else if (resizeHandle === 'sw') resizeHandle = 'se';
                else if (resizeHandle === 'se') resizeHandle = 'sw';
            }
            
            if (annotation.height < 0) {
                annotation.y += annotation.height;
                annotation.height = Math.abs(annotation.height);
                
                // 切换垂直方向的手柄
                if (resizeHandle === 'nw') resizeHandle = 'sw';
                else if (resizeHandle === 'ne') resizeHandle = 'se';
                else if (resizeHandle === 'sw') resizeHandle = 'nw';
                else if (resizeHandle === 'se') resizeHandle = 'ne';
            }
            
            // 确保不超出图片边界
            annotation.x = Math.max(0, Math.min(annotation.x, image.naturalWidth - annotation.width));
            annotation.y = Math.max(0, Math.min(annotation.y, image.naturalHeight - annotation.height));
            
            // 更新框的位置和大小
            updateAnnotationBox(annotation);
            
            // 更新列表项中的坐标信息
            const item = document.getElementById(`annotation-item-${annotation.id}`);
            if (item) {
                const coordInfo = item.querySelector('small');
                if (coordInfo) {
                    coordInfo.textContent = `(${Math.round(annotation.x)}, ${Math.round(annotation.y)}, ${Math.round(annotation.width)}, ${Math.round(annotation.height)})`;
                }
            }
            
            // 更新标注状态为"未保存"
            const annotationStatus = document.getElementById('annotation-status');
            if (annotationStatus) {
                annotationStatus.className = 'badge bg-warning';
                annotationStatus.textContent = '未保存';
            }
            
            // 标记为有未保存的更改
            hasUnsavedChanges = true;
        }
    }
}

// 鼠标释放事件处理
function handleMouseUp(e) {
    if (isDrawing && currentBox) {
        // 获取框的位置和大小
        const rect = currentBox.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        // 计算相对于容器的坐标
        const x = (rect.left - containerRect.left) / currentScale;
        const y = (rect.top - containerRect.top) / currentScale;
        const width = rect.width / currentScale;
        const height = rect.height / currentScale;
        
        // 如果框太小，则忽略
        if (width < 5 || height < 5) {
            canvas.removeChild(currentBox);
            currentBox = null;
            isDrawing = false;
            return;
        }
        
        // 移除临时绘制类
        currentBox.classList.remove('drawing');
        
        // 创建新的标注对象
        const annotation = {
            id: nextAnnotationId++,
            x: x,
            y: y,
            width: width,
            height: height
        };
        
        // 保存临时标注
        currentAnnotation = annotation;
        
        // 显示标签选择模态框
        showLabelSelectionModal(annotation);
    }
    
    // 重置状态
    isDrawing = false;
    isDragging = false;
    isResizing = false;
    resizeHandle = null;
}

// 鼠标离开容器
function handleMouseLeave(e) {
    // 如果正在绘制，取消绘制
    if (isDrawing && currentBox) {
        canvas.removeChild(currentBox);
        currentBox = null;
        isDrawing = false;
    }
    
    // 重置状态
    isDragging = false;
    isResizing = false;
    resizeHandle = null;
}

// 创建标注框
function createAnnotationBox(annotation) {
    // 移除现有的框
    const existingBox = document.getElementById(`box-${annotation.id}`);
    if (existingBox) {
        canvas.removeChild(existingBox);
    }
    
    // 创建新的框
    const box = document.createElement('div');
    box.className = 'annotation-box';
    box.id = `box-${annotation.id}`;
    box.style.left = annotation.x + 'px';
    box.style.top = annotation.y + 'px';
    box.style.width = annotation.width + 'px';
    box.style.height = annotation.height + 'px';
    box.style.borderColor = annotation.label_color || '#FF0000';
    
    // 添加标签
    if (annotation.label_name) {
        const label = document.createElement('div');
        label.className = 'annotation-label';
        label.textContent = annotation.label_name;
        label.style.backgroundColor = annotation.label_color;
        box.appendChild(label);
    }
    
    // 添加调整大小的手柄
    const handles = ['nw', 'ne', 'sw', 'se'];
    handles.forEach(position => {
        const handle = document.createElement('div');
        handle.className = `resize-handle ${position}`;
        box.appendChild(handle);
    });
    
    // 点击选中
    box.addEventListener('mousedown', function(e) {
        // 阻止事件冒泡，避免触发画布的mousedown事件
        e.stopPropagation();
        
        // 检查是否点击了调整大小的手柄
        const handles = box.querySelectorAll('.resize-handle');
        let clickedHandle = null;
        
        handles.forEach(handle => {
            const handleRect = handle.getBoundingClientRect();
            if (e.clientX >= handleRect.left && e.clientX <= handleRect.right &&
                e.clientY >= handleRect.top && e.clientY <= handleRect.bottom) {
                clickedHandle = handle;
            }
        });
        
        if (clickedHandle) {
            // 开始调整大小
            isResizing = true;
            resizeHandle = clickedHandle.className.split(' ')[1]; // 获取方向 (nw, ne, sw, se)
            selectAnnotation(annotation.id);
        } else {
            // 开始拖动
            isDragging = true;
            selectAnnotation(annotation.id);
        }
        
        // 获取鼠标相对于容器的坐标
        const rect = container.getBoundingClientRect();
        startX = (e.clientX - rect.left) / currentScale;
        startY = (e.clientY - rect.top) / currentScale;
    });
    
    // 添加到画布
    canvas.appendChild(box);
    
    // 标记为有未保存的更改
    hasUnsavedChanges = true;
    
    return box;
}

// 选中标注
function selectAnnotation(id) {
    // 如果已经选中，不做任何操作
    if (selectedAnnotationId === id) {
        return;
    }
    
    // 取消之前选中的标注
    if (selectedAnnotationId !== null) {
        const prevBox = document.getElementById(`box-${selectedAnnotationId}`);
        if (prevBox) {
            prevBox.classList.remove('selected');
        }
        
        const prevItem = document.getElementById(`annotation-item-${selectedAnnotationId}`);
        if (prevItem) {
            prevItem.classList.remove('active');
        }
    }
    
    // 选中新的标注
    selectedAnnotationId = id;
    
    // 高亮显示框
    const box = document.getElementById(`box-${id}`);
    if (box) {
        box.classList.add('selected');
    }
    
    // 高亮显示列表项
    const item = document.getElementById(`annotation-item-${id}`);
    if (item) {
        item.classList.add('active');
        
        // 滚动到可见区域
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // 启用删除按钮
    if (deleteButton) {
        deleteButton.disabled = false;
    }
}

// 取消选中
function deselectAnnotation() {
    if (selectedAnnotationId === null) {
        return;
    }
    
    // 移除高亮
    const box = document.getElementById(`box-${selectedAnnotationId}`);
    if (box) {
        box.classList.remove('selected');
    }
    
    const item = document.getElementById(`annotation-item-${selectedAnnotationId}`);
    if (item) {
        item.classList.remove('active');
    }
    
    // 重置选中状态
    selectedAnnotationId = null;
    
    // 禁用删除按钮
    if (deleteButton) {
        deleteButton.disabled = true;
    }
}

// 删除选中的标注
function deleteSelectedAnnotation() {
    if (selectedAnnotationId === null) {
        console.log('没有选中的标注');
        return;
    }
    
    console.log('删除标注:', selectedAnnotationId);
    
    // 删除标注框
    const box = document.getElementById(`box-${selectedAnnotationId}`);
    if (box) {
        canvas.removeChild(box);
    }
    
    // 删除列表项
    const item = document.getElementById(`annotation-item-${selectedAnnotationId}`);
    if (item) {
        annotationList.removeChild(item);
    }
    
    // 从数组中删除
    const index = annotations.findIndex(a => a.id === selectedAnnotationId);
    if (index !== -1) {
        annotations.splice(index, 1);
    }
    
    // 重置选中状态
    selectedAnnotationId = null;
    
    // 禁用删除按钮
    if (deleteButton) {
        deleteButton.disabled = true;
    }
    
    // 更新标签计数
    updateLabelCounts();
    
    // 更新总标注数
    if (document.getElementById('total-annotations-count')) {
        document.getElementById('total-annotations-count').textContent = annotations.length;
    }
    
    // 如果没有标注，显示提示
    if (annotations.length === 0 && noAnnotationsMessage) {
        noAnnotationsMessage.style.display = 'block';
    }
    
    // 更新标注状态为"未保存"
    const annotationStatus = document.getElementById('annotation-status');
    if (annotationStatus) {
        annotationStatus.className = 'badge bg-warning';
        annotationStatus.textContent = '未保存';
    }
    
    // 标记为有未保存的更改
    hasUnsavedChanges = true;
}

// 清除所有标注
function clearAnnotations() {
    if (confirm('确定要清除所有标注吗？此操作不可撤销。')) {
        // 清空画布
        while (canvas.firstChild) {
            canvas.removeChild(canvas.firstChild);
        }
        
        // 清空列表
        while (annotationList.firstChild) {
            annotationList.removeChild(annotationList.firstChild);
        }
        
        // 清空数组
        annotations = [];
        
        // 重置选中状态
        selectedAnnotationId = null;
        
        // 禁用删除按钮
        if (deleteButton) {
            deleteButton.disabled = true;
        }
        
        // 显示"没有标注"的提示
        if (noAnnotationsMessage) {
            noAnnotationsMessage.style.display = 'block';
        }
        
        // 重置标签计数
        updateLabelCounts();
        
        // 标记为有未保存的更改
        hasUnsavedChanges = true;
    }
}

// 更新标签计数
function updateLabelCounts() {
    // 重置所有计数
    document.querySelectorAll('.label-count').forEach(count => {
        count.textContent = '0';
    });
    
    // 统计每个标签的使用次数
    annotations.forEach(annotation => {
        if (annotation.label_id) {
            const countElement = document.querySelector(`.label-count[data-label-id="${annotation.label_id}"]`);
            if (countElement) {
                const currentCount = parseInt(countElement.textContent);
                countElement.textContent = currentCount + 1;
            }
        }
    });
    
    // 更新总标注数
    const totalCount = document.getElementById('total-annotations-count');
    if (totalCount) {
        totalCount.textContent = annotations.length;
    }
}

// 缩放功能
function zoomIn() {
    currentScale = Math.min(currentScale * 1.2, 5);
    applyZoom();
}

function zoomOut() {
    currentScale = Math.max(currentScale / 1.2, 0.2);
    applyZoom();
}

function resetZoom() {
    currentScale = 1;
    applyZoom();
}

function applyZoom() {
    image.style.transform = `scale(${currentScale})`;
    canvas.style.transform = `scale(${currentScale})`;
    
    // 更新所有标注框的位置和大小
    annotations.forEach(updateAnnotationBox);
}

// 当绘制完成时，显示标签选择模态框
function showLabelSelectionModal(annotation) {
    // 显示模态框
    labelModal.show();
    
    // 设置点击事件
    document.querySelectorAll('#labelSelectionModal .label-item').forEach(item => {
        item.onclick = function() {
            // 获取标签信息
            const labelId = parseInt(this.dataset.labelId);
            const labelName = this.dataset.labelName;
            const labelColor = this.dataset.labelColor;
            
            // 更新标注数据
            annotation.label_id = labelId;
            annotation.label_name = labelName;
            annotation.label_color = labelColor;
            
            // 更新标注框
            updateAnnotationBox(annotation);
            
            // 更新标注列表项
            createAnnotationListItem(annotation);
            
            // 更新标签计数
            updateLabelCounts();
            
            // 关闭模态框
            labelModal.hide();
        };
    });
}

// 保存标注
function saveAnnotations() {
    console.log('开始保存标注...');
    
    // 准备要发送的数据
    const data = {
        annotations: annotations.map(a => ({
            label_id: a.label_id,
            x: Math.round(a.x),
            y: Math.round(a.y),
            width: Math.round(a.width),
            height: Math.round(a.height)
        }))
    };
    
    console.log('标注数据:', data);
    console.log('图片ID:', imageId);
    console.log('保存URL:', saveUrl);
    
    // 更新总标注数
    document.getElementById('total-annotations-count').textContent = annotations.length;
    
    // 显示保存中状态
    saveButton.disabled = true;
    saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 保存中...';
    
    // 更新标注状态为"保存中"
    const annotationStatus = document.getElementById('annotation-status');
    if (annotationStatus) {
        annotationStatus.className = 'badge bg-info';
        annotationStatus.textContent = '保存中...';
    }
    
    // 发送到服务器
    fetch(saveUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('服务器响应状态:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('服务器响应数据:', data);
        
        if (data.status === 'success') {
            // 保存成功，更新状态为"已保存"
            if (annotationStatus) {
                annotationStatus.className = 'badge bg-success';
                annotationStatus.textContent = '已保存';
            }
            
            // 更新任务列表中的标注状态（如果在同一页面）
            if (typeof imageId !== 'undefined') {
                const taskListItem = document.querySelector(`tr[data-image-id="${imageId}"] .badge`);
                console.log('查找标注状态元素:', `tr[data-image-id="${imageId}"] .badge`, taskListItem);
                
                if (taskListItem) {
                    taskListItem.className = 'badge bg-success';
                    taskListItem.textContent = '已标注';
                }
            }
            
            // 标记为已保存状态，防止离开页面时提示
            hasUnsavedChanges = false;
            
            // 如果有下一张图片，自动跳转
            const nextButton = document.querySelector('a.btn-outline-primary[href*="annotate_image"]:not([disabled])');
            if (nextButton && autoNext) {
                console.log('自动跳转到下一张图片');
                nextButton.click();
            }
        } else {
            // 保存失败，更新状态为"保存失败"
            if (annotationStatus) {
                annotationStatus.className = 'badge bg-danger';
                annotationStatus.textContent = '保存失败';
            }
            
            // 显示错误消息
            console.error('保存失败:', data.message);
            alert('保存失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('保存标注时发生错误:', error);
        
        // 发生错误，更新状态为"保存失败"
        if (annotationStatus) {
            annotationStatus.className = 'badge bg-danger';
            annotationStatus.textContent = '保存失败';
        }
        
        alert('保存标注时发生错误: ' + error.message);
    })
    .finally(() => {
        // 恢复按钮状态
        saveButton.disabled = false;
        saveButton.innerHTML = '<i class="bi bi-save"></i> 保存标注';
        console.log('保存操作完成');
    });
}

// 更新标注框
function updateAnnotationBox(annotation) {
    const box = document.getElementById(`box-${annotation.id}`);
    if (!box) return;
    
    // 更新位置和大小
    box.style.left = annotation.x + 'px';
    box.style.top = annotation.y + 'px';
    box.style.width = annotation.width + 'px';
    box.style.height = annotation.height + 'px';
    
    // 更新边框颜色
    box.style.borderColor = annotation.label_color || '#FF0000';
    
    // 更新或添加标签
    let label = box.querySelector('.annotation-label');
    if (annotation.label_name) {
        if (!label) {
            label = document.createElement('div');
            label.className = 'annotation-label';
            box.appendChild(label);
        }
        label.textContent = annotation.label_name;
        label.style.backgroundColor = annotation.label_color;
    } else if (label) {
        box.removeChild(label);
    }
    
    // 确保有调整大小的手柄
    const handles = ['nw', 'ne', 'sw', 'se'];
    handles.forEach(position => {
        let handle = box.querySelector(`.resize-handle.${position}`);
        if (!handle) {
            handle = document.createElement('div');
            handle.className = `resize-handle ${position}`;
            box.appendChild(handle);
        }
    });
    
    // 标记为有未保存的更改
    hasUnsavedChanges = true;
}

// 创建标注列表项
function createAnnotationListItem(annotation) {
    // 移除现有的列表项
    const existingItem = document.getElementById(`annotation-item-${annotation.id}`);
    if (existingItem) {
        existingItem.remove();
    }
    
    // 创建新的列表项
    const item = document.createElement('div');
    item.className = 'list-group-item d-flex justify-content-between align-items-center';
    item.id = `annotation-item-${annotation.id}`;
    
    // 标签信息
    const labelInfo = document.createElement('div');
    labelInfo.className = 'd-flex align-items-center';
    
    if (annotation.label_name) {
        const colorBox = document.createElement('span');
        colorBox.className = 'color-box';
        colorBox.style.backgroundColor = annotation.label_color;
        labelInfo.appendChild(colorBox);
        
        const labelName = document.createElement('span');
        labelName.textContent = annotation.label_name;
        labelInfo.appendChild(labelName);
    } else {
        const noLabel = document.createElement('span');
        noLabel.className = 'text-muted';
        noLabel.textContent = '未设置标签';
        labelInfo.appendChild(noLabel);
    }
    
    item.appendChild(labelInfo);
    
    // 坐标信息
    const coordInfo = document.createElement('small');
    coordInfo.className = 'text-muted';
    coordInfo.textContent = `(${annotation.x}, ${annotation.y}, ${annotation.width}, ${annotation.height})`;
    item.appendChild(coordInfo);
    
    // 点击选中
    item.addEventListener('click', function() {
        selectAnnotation(annotation.id);
    });
    
    // 添加到列表
    annotationList.appendChild(item);
    
    // 隐藏"没有标注"的提示
    if (noAnnotationsMessage) {
        noAnnotationsMessage.style.display = 'none';
    }
    
    return item;
}

// 键盘事件处理
function handleKeyDown(e) {
    console.log('键盘事件:', e.key);
    
    // Delete 键删除选中的标注
    if (e.key === 'Delete' && selectedAnnotationId !== null) {
        console.log('删除选中的标注:', selectedAnnotationId);
        deleteSelectedAnnotation();
    }
    
    // Escape 键取消当前操作
    if (e.key === 'Escape') {
        // 取消绘制
        if (isDrawing && currentBox) {
            console.log('取消绘制');
            canvas.removeChild(currentBox);
            currentBox = null;
            isDrawing = false;
        }
        
        // 取消选中
        if (selectedAnnotationId !== null) {
            console.log('取消选中');
            deselectAnnotation();
        }
    }
    
    // Ctrl+S 保存标注
    if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault(); // 阻止浏览器默认的保存页面行为
        console.log('保存标注');
        saveAnnotations();
    }
    
    // 左右箭头切换图片
    if (e.key === 'ArrowLeft') {
        const prevButton = document.querySelector('a.btn-outline-primary[href*="annotate_image"]:not([disabled]):first-of-type');
        if (prevButton) {
            console.log('切换到上一张图片');
            prevButton.click();
        }
    }
    
    if (e.key === 'ArrowRight') {
        const nextButton = document.querySelector('a.btn-outline-primary[href*="annotate_image"]:not([disabled]):last-of-type');
        if (nextButton) {
            console.log('切换到下一张图片');
            nextButton.click();
        }
    }
    
    // +/- 缩放
    if (e.key === '+' || e.key === '=') {
        console.log('放大');
        zoomIn();
    }
    
    if (e.key === '-' || e.key === '_') {
        console.log('缩小');
        zoomOut();
    }
    
    // 0 重置缩放
    if (e.key === '0') {
        console.log('重置缩放');
        resetZoom();
    }
} 
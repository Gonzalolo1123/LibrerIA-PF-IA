// CRUD y renderizado de productos IA para consulta inteligente

let productoAEliminar = null;

document.addEventListener('DOMContentLoaded', function() {
    renderTablaProductos();
    asignarEventosCRUD();
});

function asignarEventosCRUD() {
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.onclick = function() {
            modificarProducto(this.getAttribute('data-index'));
        };
    });
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.onclick = function() {
            eliminarProducto(this.getAttribute('data-index'));
        };
    });
}

function renderTablaProductos() {
    const tbody = document.querySelector('.table tbody');
    const tfootTotal = document.getElementById('totalEstimado');
    tbody.innerHTML = '';
    let total = 0;
    productos.forEach((p, i) => {
        const nombre = p.producto ?? '-';
        const marca = p.marca ?? '-';
        const calidad = p.calidad ?? 'No especificado';
        const precio = (p.precio !== null && p.precio !== undefined) ? p.precio : '-';
        const stock = (p.stock !== null && p.stock !== undefined) ? p.stock : '-';
        const cantidad = (p.cantidad_sugerida !== null && p.cantidad_sugerida !== undefined) ? p.cantidad_sugerida : 1;
        const subtotal = (typeof precio === 'number' ? precio : 0) * (typeof cantidad === 'number' ? cantidad : 1);
        total += (typeof subtotal === 'number' ? subtotal : 0);
        tbody.innerHTML += `
        <tr class="item-row">
            <td>${i + 1}</td>
            <td><strong>${nombre}</strong></td>
            <td>${marca}</td>
            <td><span class="badge bg-info">${calidad}</span></td>
            <td><span class="price">$${precio}</span></td>
            <td>${stock}</td>
            <td><span class="badge bg-primary">${cantidad}</span></td>
            <td>
                <button class="btn btn-outline-secondary btn-sm btn-editar" data-index="${i}"><i class="fas fa-edit"></i></button>
                <button class="btn btn-outline-danger btn-sm btn-eliminar" data-index="${i}"><i class="fas fa-trash"></i></button>
            </td>
        </tr>`;
    });
    if (tfootTotal) {
        tfootTotal.textContent = `$${total}`;
    }
    asignarEventosCRUD();
}

function showToast(mensaje, tipo = 'primary') {
    const toast = new bootstrap.Toast(document.getElementById('toastMensaje'));
    const toastDiv = document.getElementById('toastMensaje');
    const toastTexto = document.getElementById('toastMensajeTexto');
    toastDiv.className = `toast align-items-center text-bg-${tipo} border-0`;
    toastTexto.textContent = mensaje;
    toast.show();
}

function agregarProducto() {
    document.getElementById('modalProductoLabel').textContent = 'Agregar producto';
    document.getElementById('formProducto').reset();
    document.getElementById('inputIndex').value = '';
    var modal = new bootstrap.Modal(document.getElementById('modalProducto'));
    modal.show();
}

function modificarProducto(index) {
    const p = productos[index];
    document.getElementById('modalProductoLabel').textContent = 'Modificar producto';
    document.getElementById('inputProducto').value = p.producto;
    document.getElementById('inputMarca').value = p.marca;
    document.getElementById('inputCalidad').value = p.calidad;
    document.getElementById('inputPrecio').value = p.precio;
    document.getElementById('inputStock').value = p.stock;
    document.getElementById('inputCantidad').value = p.cantidad_sugerida;
    document.getElementById('inputIndex').value = index;
    var modal = new bootstrap.Modal(document.getElementById('modalProducto'));
    modal.show();
}

function eliminarProducto(index) {
    productoAEliminar = index;
    const p = productos[index];
    document.getElementById('textoEliminar').textContent = `¿Estás seguro de que quieres eliminar el producto "${p.producto}"?`;
    var modal = new bootstrap.Modal(document.getElementById('modalEliminar'));
    modal.show();
}

document.getElementById('btnGuardarProducto').onclick = function() {
    const nombre = document.getElementById('inputProducto').value.trim();
    const marca = document.getElementById('inputMarca').value.trim();
    const calidad = document.getElementById('inputCalidad').value.trim();
    const precio = parseInt(document.getElementById('inputPrecio').value);
    const stock = parseInt(document.getElementById('inputStock').value);
    const cantidad = parseInt(document.getElementById('inputCantidad').value);
    const index = document.getElementById('inputIndex').value;
    if (!nombre || !marca || !calidad || isNaN(precio) || isNaN(stock) || isNaN(cantidad)) {
        showToast('Por favor completa todos los campos correctamente.', 'danger');
        return;
    }
    const nuevoProducto = {
        producto: nombre,
        marca: marca,
        calidad: calidad,
        precio: precio,
        stock: stock,
        cantidad_sugerida: cantidad
    };
    if (index === '') {
        productos.push(nuevoProducto);
        showToast('Producto agregado exitosamente.', 'success');
    } else {
        productos[index] = nuevoProducto;
        showToast('Producto modificado exitosamente.', 'info');
    }
    renderTablaProductos();
    bootstrap.Modal.getInstance(document.getElementById('modalProducto')).hide();
};

document.getElementById('btnConfirmarEliminar').onclick = function() {
    if (productoAEliminar !== null) {
        productos.splice(productoAEliminar, 1);
        renderTablaProductos();
        showToast('Producto eliminado.', 'warning');
        productoAEliminar = null;
        bootstrap.Modal.getInstance(document.getElementById('modalEliminar')).hide();
    }
}; 
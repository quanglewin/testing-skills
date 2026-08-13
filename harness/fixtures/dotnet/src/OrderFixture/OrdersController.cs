using Microsoft.AspNetCore.Mvc;

namespace OrderFixture;

[ApiController]
[Route("orders")]
public class OrdersController(IOrderService orderService) : ControllerBase
{
    [HttpGet("{id}")]
    public IActionResult GetOrder(string id)
    {
        try
        {
            return Ok(orderService.GetOrder(id));
        }
        catch (OrderNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost]
    public IActionResult CreateOrder(OrderRequest request)
    {
        try
        {
            Order order = orderService.CreateOrder(request);
            return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
    }
}
